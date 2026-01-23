"""
Generates the DED for a specific module. To use,
scroll to the bottom main and update the
`module`, `visit`, and `output_filename` variables.

EXTRA STEPS:
1) For LBD, you need to copy the `header` directory to
   the long and short directories as well (just don't
   check it in).
"""
import argparse
import logging
import os
import pandas as pd
import csv
from datetime import datetime

from convert_to_utf8 import convert_to_utf8
from form_organizer import FormOrganizer
from module_configurations import *

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


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


class DedGenerator(FormOrganizer):
    """Class for generating the DED."""

    def __init__(self, module: str, visit: str):
        """Set classification to QNV CSVs and initialize empty DFs"""
        super().__init__(module, visit, FileClassification.QNV)

        self.combined_df = pd.DataFrame(dtype=object)
        self.header_df = None

    def execute(self, subdir: str, file: str, file_found: bool, override_visit: str = None) -> bool:
        """If a valid Q&V CSV for the visit, concat to the DED

        Args:
            subdir: The subdirectory containing this file
            file: The file to maybe add to the DED
            file_found: Whether or not we've found a Q&V for this form yet
            override_visit: The override visit

        Returns:
            True if the Q&V was found, False otherwise
        """
        visit = None
        if override_visit:
            visit = override_visit
        elif self.visit:
            visit = self.visit.value

        if not self.is_correct_file(file, visit):
            return file_found  # return previous state

        # found the form, will always return True after this point
        try:
            file_path = os.path.join(subdir, file)
            log.info(f"Adding {file_path}")

            # Read the csv file into a DataFrame - if not UTF-8, convert
            try:
                df = pd.read_csv(file_path, dtype=object, encoding='utf-8')
            except UnicodeDecodeError:
                convert_to_utf8(file_path, file_path)
                df = pd.read_csv(file_path, dtype=object, encoding='utf-8')

            # Remove rows with NaN in 'form_name' column
            df = df.dropna(subset=['form_name'])

            # Remove empty rows
            df = df.dropna(how='all')

            # Remove newline characters from all values
            df = df.map(clean_newlines)

            # Convert variable names to lowercase
            df['var_name'] = df['var_name'].str.lower()

            # ensure packet is consistent (some FVPs pull directly from the IVP file)
            if 'packet' in df.columns and self.module in PACKET_MAPPING and self.visit:
                df['packet'] = PACKET_MAPPING[self.module][self.visit]

            # Append the data to the combined DataFrame
            if 'header' in file:
                log.info(f"Found header file: {file}")
                if self.header_df:
                    raise ValueError("Multiple header DFs found")

                self.header_df = df
                return True
            else:
                self.combined_df = pd.concat(
                    [self.combined_df, df], ignore_index=True)
        except Exception as e:
            log.warning(f'File {file_path} threw an exception: {e}')

        return True

    def handle_lbd_short_fvp(self, form: str, subdir: str, long_subdir: str, file_found: bool) -> bool:
        """Handles FVP LBD_SHORT specifically for DED generation. These will try to pull
        from LBD Long FVP then LBD Long IVP.

        Args:
            form: The form name
            subdir: The short subdirectory - not used here
            long_subdir: The long subdirectory
            file_found: Whether or not the file was found

        Returns:
            Whether or not the file was found
        """
        if form in STATIC_LBD_FORMS:
            for file in os.listdir(long_subdir):
                file_found = self.execute(long_subdir, file, file_found,
                                          override_visit=VisitType.FVP)
            if not file_found:
                for file in os.listdir(long_subdir):
                    file_found = self.execute(long_subdir, file, file_found,
                                              override_visit=VisitType.IVP)

        return file_found

    def generate(self, output_filename: str) -> None:
        """Generate the DED.

        Args:
            output_filename: Name of the output file to write results to
        """
        self.run()

        # Concat header to beginning of the DF (forms without packets do not have headers)
        if self.header_df is None and self.module.has_packet():
            log.warning(f"No header file found for {self.module}")

        self.combined_df = pd.concat(
            [self.header_df, self.combined_df], ignore_index=True)

        # Ensure the output directory exists
        ensure_directory_exists(output_filename)

        # Export the combined DataFrame to a CSV file
        self.combined_df.to_csv(
            output_filename, index=False, quoting=csv.QUOTE_MINIMAL)
        log.info(f"DED file saved as {output_filename}")


def generate_ded(module: ModuleType,
                 visit: VisitType | None = None,
                 target_dir: str = './work/combined_ded',
                 target_date: str = None) -> str:
    """Generate the DED.

    Filename follows module-version-packet-ded-date.csv format
    """
    module_name = module.value
    formver = FORM_VER_MAPPING.get(module)
    if not formver:
        raise ValueError(f"no formver found for {module.value}")

    if not target_date:
        target_date = datetime.today().strftime("%m%d%Y")

    if module.value in [ModuleType.LBD_LONG.value, ModuleType.LBD_SHORT.value]:
        # long/short lbd determined by version in naming scheme
        module_name = "lbd"
    else:
        # all formvers reduce to ints unless LBD
        formver = str(int(float(formver)))

        # also update module names for enrollment
        if module.value == ModuleType.ENROLLMENT.value:
            module_name = "enroll"

    if visit:
        filename = f"{module_name}-v{formver}-{visit.value}-ded-{target_date}.csv"
    else:
        filename = f"{module_name}-v{formver}-ded-{target_date}.csv"

    filename = f'{target_dir}/{filename}'
    log.info(f"Generating DED {filename}")

    generator = DedGenerator(module=module, visit=visit)
    generator.generate(filename)
    return filename


def main():
    parser = argparse.ArgumentParser(prog='Generates DEDs')
    parser.add_argument('-m', '--modules', dest='modules', type=str, required=True,
                        help="Comma-deliminated list of modules to generate DED(s) for. "
                        + "Will generate a DED for all relevant visits (e.g. IVP/FVP)")
    parser.add_argument('-o', '--output-dir', dest='output_dir', type=str, required=True,
                        help="Target output directory to write results to")
    parser.add_argument('-d', '--target-date', dest='target_date', type=str, required=False,
                        help="Target date (in MMDDYYYY format) to use for DED filenames; "
                             + "defaults to today if not specified")

    args = parser.parse_args()
    modules = args.modules.lower()
    log.info(f"modules:\t{modules}")

    for raw_module in modules.split(','):
        module = ModuleType(raw_module.strip())

        # Skip legacy DS module (no change in DED)
        if module.value == 'ds/legacy':
            continue

        for visit in PACKET_MAPPING.get(module, [None]):
            # ignore I4 packets
            if visit == VisitType.I4:
                continue

            generate_ded(module, visit, args.output_dir, args.target_date)


if __name__ == "__main__":
    main()
