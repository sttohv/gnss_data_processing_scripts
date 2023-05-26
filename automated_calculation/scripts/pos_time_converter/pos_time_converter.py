import csv
import os
import datetime
from pathlib import Path


def convert_GPST_to_time(location="Tudengimaja", device="Pixel", date="13_05"):
    filepaths = get_files(date, device, location)

    output_file_path = filepaths[0]
    input_file_path = filepaths[1]

    with open(output_file_path, 'w', newline='') as f:
        writer = csv.writer(f)

        header = ["time", "latitude", "longitude"]
        writer.writerow(header)

        stream = open(input_file_path, 'r')
        for line in stream:
            if line[0].isdigit():
                line_list = line.split("   ")
                gps_time = line_list[0]
                time = get_time_from_GPST(gps_time)
                latitude = line_list[1]
                longitude = line_list[2].split()[0]
                row = [time, latitude, longitude]
                writer.writerow(row)


def get_time_from_GPST(gpst: str) -> str:
    splited_GPST = gpst.split(" ")
    weeks = int(splited_GPST[0])
    seconds = int(splited_GPST[1][:-4])
    # Constants from the formula
    minus_seconds = 18

    # Calculate the new date
    new_date = datetime.datetime(1980, 1, 6) + datetime.timedelta(weeks=weeks, seconds=(seconds - minus_seconds))
    formatted_result = new_date.strftime("%H:%M:%S")
    return formatted_result


def get_files(date, device, location):
    # Get the current file location
    current_script_path = os.path.realpath(__file__)
    # Get the base directory
    base_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

    # Set input and output directories
    input_directory = os.path.join(base_directory, "input", date)
    output_directory = os.path.join(base_directory, "output", f"{date}")

    input_path = Path(input_directory)
    input_file_names = [file.name for file in input_path.iterdir() if file.is_file() and file.suffix == ".pos"]

    input_filename = input_file_names[0]
    output_filename = f"{device}_pos_{date}_{location}.csv"

    os.makedirs(output_directory, exist_ok=True)

    output_file_path = os.path.join(output_directory, output_filename)
    input_file_path = os.path.join(input_directory, input_filename)
    return output_file_path, input_file_path


if __name__ == "__main__":
    convert_GPST_to_time()
