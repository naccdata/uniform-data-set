
import os
import pandas as pd
import csv

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

def main(root_directory, output_filename):
    # Initialize an empty DataFrame
    combined_df = pd.DataFrame(dtype=object)

    # Walk through the directory
    for subdir, _, files in os.walk(root_directory):
        for file in files:
            # Check if the filename matches the pattern
            if 'form_' in file and '_questions_' in file and file.endswith('.csv'):
                try:
                    file_path = os.path.join(subdir, file)
                    # Read the csv file into a DataFrame
                    df = pd.read_csv(file_path, dtype=object)
                    # Remove rows with NaN in 'form_name' column
                    df = df.dropna(subset=['form_name'])
                    # Remove newline characters from all values
                    df = df.map(clean_newlines)
                    # Append the data to the combined DataFrame
                    combined_df = pd.concat([combined_df, df], ignore_index=True,)
                except Exception as e:
                    print(f'File {file} threw an exception: {e}')

    # Ensure the output directory exists
    ensure_directory_exists(output_filename)
    # Export the combined DataFrame to a CSV file
    combined_df.to_csv(output_filename, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Combined CSV file saved as {output_filename}")

if __name__ == "__main__":
    root_directory = '../../forms/uds'
    output_filename = './combined_ded/combined_questions.csv'
    main(root_directory, output_filename)