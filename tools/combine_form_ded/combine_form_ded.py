"""
Generates the DED for a specific module. To use,
scroll to the bottom main and update the
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
from datetime import date

from form_organizer import (
    FileClassification,
    FormOrganizer,
    ModuleType,
    VisitType
)

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

    def __init__(self, root_dir: str, module: str, visit: str):
        """Set classification to QNV CSVs and initialize empty DFs"""
        super().__init__(root_dir, module, visit, FileClassification.QNV)

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
        visit = override_visit if override_visit else self.visit
        if not self.is_correct_file(file, visit):
            return file_found  # return previous state

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
                if self.header_df:
                    raise ValueError("Multiple header DFs found")

                self.header_df = df
                return True
            else:
                self.combined_df = pd.concat([self.combined_df, df], ignore_index=True)
        except Exception as e:
            log.warning(f'File {file_path} threw an exception: {e}')

        return True

    def generate(self, output_filename: str) -> None:
        """Generate the DED.

        Args:
            output_filename: Name of the output file to write results to
        """
        self.run()

        # Concat header to beginning of the DF (if not enrollment form)
        if self.header_df is None and self.module != ModuleType.ENROLLMENT:
            raise ValueError(f"No header file found for {self.module}")
        self.combined_df = pd.concat([self.header_df, self.combined_df], ignore_index=True)

        # Ensure the output directory exists
        ensure_directory_exists(output_filename)

        # Export the combined DataFrame to a CSV file
        self.combined_df.to_csv(output_filename, index=False, quoting=csv.QUOTE_MINIMAL)
        log.info(f"Combined CSV file saved as {output_filename}")


if __name__ == "__main__":

    # CHANGE THESE
    # If LBD, make sure the LBD long/short directories each have
    # their own copy of the header files before running
    module = ModuleType.UDS
    visit = VisitType.IVP
    output_filename = f'./combined_ded/{date.today()}_uds_ivp_ded.csv'

    generator = DedGenerator(
        root_dir='../../forms',
        module=module,
        visit=visit)

    generator.generate(output_filename)
