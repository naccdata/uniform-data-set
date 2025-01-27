"""
Generates the DED for a specific module. To use,
scroll to the bottom __main__ and update the
`module`, `visit`, and `output_filename` variables.

EXTRA STEPS:

1) For LBD, you need to copy the `header` directory to
   the long and short directories as well (just don't
   check it in).
2) For FVP, you need to manually replace the packets
   since most will pull from the IVP packet
   e.g. in the raw CSV, ctrl-f for `,IF,` and replace with `,FF,`
        note the commas to avoid accidentally replacing something unrelated
"""
import logging
import os
import pandas as pd
import csv

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class VisitType:
    IVP = 'ivp'
    FVP = 'fvp'


class ModuleType:
    UDS = 'uds'
    FTLD = 'ftld'
    LBD_LONG = 'lbd/long'
    LBD_SHORT = 'lbd/short'


def ensure_directory_exists(file_path: str) -> None:
    # Get the directory name from the file path
    directory = os.path.dirname(file_path)
    # Create the directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)


def clean_newlines(value: str) -> str:
    # Replace newline characters with an empty string
    if isinstance(value, str):
        return value.replace('\n', '').replace('\r', '')
    return value


class DedGenerator:
    """Class for generating the DED."""

    def __init__(self, root_dir: str, module: str, visit: str):
        """Initialize empty DFs"""
        self.__root_dir = f'{root_dir}/{module}'
        self.__module = module
        self.__visit = visit

        self.__combined_df = pd.DataFrame(dtype=object)
        self.__header_df = None

    def concat_form(self, subdir: str, file: str, qnv_found: bool, override_visit: str = None) -> bool:
        """If a valid Q&V CSV for the visit, concat to the DED

        Args:
            subdir: The subdirectory containing this file
            file: The file to maybe add to the DED
            qnv_found: Whether or not we've found a Q&V for this form yet
            override_visit: The override visit

        Returns:
            True if the Q&V was found, False otherwise
        """
        visit = override_visit if override_visit else self.__visit
        # Check if the filename matches the pattern
        if (not file.endswith('.csv')        # not a CSV
            or not file.startswith('form_')  # not a form CSV
            or '_questions_' not in file     # not a Q&V CSV
            or f"_{visit}_" not in file):    # not a visit we care about
            return qnv_found                 # return whatever the previous state was

        # found the form, will always return True after this point
        try:
            file_path = os.path.join(subdir, file)
            log.info(f"Adding {file_path}")
            # Read the csv file into a DataFrame
            df = pd.read_csv(file_path, dtype=object)
            # Remove rows with NaN in 'form_name' column
            df = df.dropna(subset=['form_name'])
            # Remove empty rows
            df = df.dropna(how='all')
            # Remove newline characters from all values
            df = df.map(clean_newlines)
            # Convert variable names to lowercase
            df['var_name'] = df['var_name'].str.lower()
            # Append the data to the combined DataFrame
            if 'header' in file:
                log.info(f"Found header file: {file}")
                if self.__header_df:
                    raise ValueError("Multiple header DFs found")

                self.__header_df = df
                return True
            else:
                self.__combined_df = pd.concat([self.__combined_df, df], ignore_index=True)
        except Exception as e:
            log.warning(f'File {file_path} threw an exception: {e}')

        return True

    def handle_lbd(self, subdir: str, qnv_found: bool) -> bool:
        """Handle LBD, which needs to handle both the long and short case.

        Args:
            subdir: The subdirectory to search in
            qnv_found: Whether or not we've found a Q&V for this form yet
        Returns:
            Whether or not the Q&V was found
        """
        long_subdir = subdir.replace('short', 'long')
        form = subdir.split('/')[-1].strip()

        # LBD short does not have B8l, skip it by returning true so it doesn't
        # trigger other searches
        if self.__module == ModuleType.LBD_SHORT and form == 'b8l':
            return True

        # 3. For LBD Short (3.1) FVP, grab from either LBD Short IVP OR LBD Long FVP
        if self.__visit == VisitType.FVP:
            # LBD Short FVP specific case - these will try to pull from LBD Long FVP then LBD Long IVP
            if self.__module == ModuleType.LBD_SHORT:
                if form in ['b3l', 'b5l', 'b7l', 'd1l', 'e1l', 'header']:
                    for file in os.listdir(long_subdir):
                        qnv_found = self.concat_form(long_subdir, file, qnv_found,
                                                     override_visit=VisitType.FVP)
                    if not qnv_found:
                        for file in os.listdir(long_subdir):
                            qnv_found = self.concat_form(long_subdir, file, qnv_found,
                                                         override_visit=VisitType.IVP)

            # 1. In general, for any FVP, grab from the IVP directory (this case is for LBD Long FVP)
            if not qnv_found:
                for file in os.listdir(subdir):
                    qnv_found = self.concat_form(subdir, file, qnv_found,
                                                 override_visit=VisitType.IVP)

        # 2. For LBD Short (3.0) IVP, grab from LBD Long IVP
        elif self.__module == ModuleType.LBD_SHORT:
            for file in os.listdir(long_subdir):
                qnv_found = self.concat_form(long_subdir, file, qnv_found)

        # LBD Long IVP should have had its own Q&V file, so we're done here
        return qnv_found

    def generate(self, output_filename: str) -> None:
        """Generate the DED.

        Args:
            output_filename: Name of the output file to write results to
        """
        # Walk through the directory
        for subdir, dirs, files in os.walk(self.__root_dir):
            dirs.sort()  # ensures order
            qnv_found = False

            # see if the visit Q&V is defined for this module to begin with
            for file in files:
                qnv_found = self.concat_form(subdir, file, qnv_found)

            if qnv_found:
                continue

            # If not, we have to grab from a corresponding visit, e.g.
            #   1. In general, for any FVP, grab from the IVP directory
            #   2. For LBD Short (3.0) IVP, grab from LBD Long IVP
            #   3. For LBD Short (3.1) FVP, grab from either LBD Short IVP OR for special cases:
            #       - Look for LBD Long FVP
            #       - If not found, look at LBD Long IVP

            # Handle the LBD cases
            if self.__module in [ModuleType.LBD_LONG, ModuleType.LBD_SHORT]:
                qnv_found = self.handle_lbd(subdir, qnv_found)

            # everything else should be an FVP grabbing from the IVP directory; this is
            # the last case so we don't care about the result
            if not qnv_found:
                for file in os.listdir(subdir):
                    self.concat_form(subdir, file, qnv_found, override_visit=VisitType.IVP)

        # Concat header to beginning of the DF
        if self.__header_df is None:
            raise ValueError(f"No header file found for {self.__module}")
        self.__combined_df = pd.concat([self.__header_df, self.__combined_df], ignore_index=True)

        # Ensure the output directory exists
        ensure_directory_exists(output_filename)

        # Export the combined DataFrame to a CSV file
        self.__combined_df.to_csv(output_filename, index=False, quoting=csv.QUOTE_MINIMAL)
        log.info(f"Combined CSV file saved as {output_filename}")


if __name__ == "__main__":

    # CHANGE THESE
    # If LBD, make sure the LBD long/short directories each have
    # their own copy of the header files before running
    module = ModuleType.LBD_SHORT
    visit = VisitType.FVP
    output_filename = './combined_ded/output.csv'

    generator = DedGenerator(
        root_dir='../../forms',
        module=module,
        visit=visit)

    generator.generate(output_filename)
