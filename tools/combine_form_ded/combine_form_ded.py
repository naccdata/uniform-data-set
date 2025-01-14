"""
Generates the DED for a specific module. To use,
update `root_directory` and `output_filename` to the
desired values, e.g. for root_directory

UDS: ../../forms/uds
FTLD: ../../forms/ftld
3.0 LBD: ../../forms/lbd/long
3.1 LBD: ../../forms/lbd/short

NOTE: For LBD, it is easiest to copy the `header`
directory to the long and short directories as well (just
don't check it in).
"""
import logging
import os
import pandas as pd
import csv

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def ensure_directory_exists(file_path):
    # Get the directory name from the file path
    directory = os.path.dirname(file_path)
    # Create the directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)


def clean_newlines(value):
    # Replace newline characters with an empty string
    if isinstance(value, str):
        return value.replace('\n', '').replace('\r', '')
    return value


def concat_form(subdir, file, combined_df, header_df, visit: str, qnv_found: bool):
    # Check if the filename matches the pattern
    if 'form_' in file and '_questions_' in file and visit in file and file.endswith('.csv'):
        qnv_found = True
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
            # Append the data to the combined DataFrame
            if 'header' in file:
                return qnv_found, combined_df, df
            else:
                combined_df = pd.concat([combined_df, df], ignore_index=True)
        except Exception as e:
            log.warning(f'File {file_path} threw an exception: {e}')   

    return qnv_found, combined_df, header_df


def main(root_directory, output_filename, visit: str):
    # Initialize an empty DataFrame
    combined_df = pd.DataFrame(dtype=object)
    header_df = None

    # Walk through the directory
    for subdir, dirs, files in os.walk(root_directory):
        dirs.sort()  # ensures order
        qnv_found = False
        for file in files:
            qnv_found, combined_df, header_df = \
                concat_form(subdir, file, combined_df, header_df, visit, qnv_found)


        ignore_short_ivp = False
        # these will copy from 3.0 FVP, not 3.1 IVP
        if visit == '_fvp_':
            for form in ['b3l', 'b5l', 'b7l', 'd1l', 'e1l', 'header']:
                if form in subdir:
                    ignore_short_ivp = True

        if not qnv_found and visit == '_fvp_' and not ignore_short_ivp:
            # Look in IVP directory
            for file in os.listdir(subdir):
                qnv_found, combined_df, header_df = \
                    concat_form(subdir, file, combined_df, header_df, '_ivp_', qnv_found)

            # for LBD, get from long's IVP directory if not found
            if not qnv_found and 'short' in subdir and 'b8l' not in subdir:
                long_subdir = subdir.replace('short', 'long')
                for file in os.listdir(long_subdir):
                    qnv_found, combined_df, header_df = \
                        concat_form(long_subdir, file, combined_df, header_df, '_ivp_', qnv_found)
        elif not qnv_found:
            # Look in 3.0 directory
            for file in os.listdir(subdir):
                qnv_found, combined_df, header_df = \
                    concat_form(subdir, file, combined_df, header_df, visit, qnv_found)

            # for LBD, get from long directory if not found
            if not qnv_found and 'short' in subdir and 'b8l' not in subdir:
                long_subdir = subdir.replace('short', 'long')
                for file in os.listdir(long_subdir):
                    qnv_found, combined_df, header_df = \
                        concat_form(long_subdir, file, combined_df, header_df, visit, qnv_found)

            # for LBD, get from long's IVP directory if not found
            if not qnv_found and 'short' in subdir and 'b8l' not in subdir:
                long_subdir = subdir.replace('short', 'long')
                for file in os.listdir(long_subdir):
                    qnv_found, combined_df, header_df = \
                        concat_form(long_subdir, file, combined_df, header_df, '_ivp_', qnv_found)


    if header_df is not None:
        combined_df = pd.concat([header_df, combined_df], ignore_index=True)

    # Ensure the output directory exists
    ensure_directory_exists(output_filename)
    # Export the combined DataFrame to a CSV file
    combined_df.to_csv(output_filename, index=False, quoting=csv.QUOTE_MINIMAL)
    log.info(f"Combined CSV file saved as {output_filename}")

if __name__ == "__main__":
    visit = '_fvp_'
    root_directory = '../../forms/lbd/long'
    output_filename = './combined_ded/3.0_lbd_fvp_ded.csv'
    main(root_directory, output_filename, visit)
