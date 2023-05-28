import csv
import os
from pyubx2 import UBXReader, UBXMessage
from pynmeagps import NMEAMessage
from pathlib import Path

file_type = "Ground_truth"


def convert_ubx_to_csv(location="Staadion", date="13_05"):
    filepaths = get_files(date, location)

    output_file_path = filepaths[0]
    input_file_path = filepaths[1]

    with open(output_file_path, 'w', newline='') as f:
        writer = csv.writer(f)

        header = ["time", "latitude", "longitude"]
        writer.writerow(header)

        stream = open(input_file_path, 'rb')
        ubr = UBXReader(stream)

        for (raw_data, parsed_data) in ubr:
            if isinstance(parsed_data, NMEAMessage):
                if parsed_data.identity == 'GNRMC':
                    row = [parsed_data.__dict__.get('time'), parsed_data.__dict__.get('lat'),
                           parsed_data.__dict__.get('lon')]
                    writer.writerow(row)


def get_files(date, location):
    # Get the current file location
    current_script_path = os.path.realpath(__file__)
    # Get the base directory
    base_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

    # Set input and output directories
    input_directory = os.path.join(base_directory, "input", date)
    output_directory = os.path.join(base_directory, "output", f"{date}")

    input_path = Path(input_directory)
    input_file_names = [file.name for file in input_path.iterdir() if file.is_file() and file.suffix == ".ubx"]

    input_filename = input_file_names[0]
    output_filename = f"{file_type}_{date}_{location}.csv"

    os.makedirs(output_directory, exist_ok=True)

    output_file_path = os.path.join(output_directory, output_filename)
    input_file_path = os.path.join(input_directory, input_filename)
    return output_file_path, input_file_path


if __name__ == "__main__":
    convert_ubx_to_csv()
