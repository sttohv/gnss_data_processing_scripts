import os
from pathlib import Path


def gpst_to_utc(gps_time_nanos):
    gps_time_millis = gps_time_nanos / 1e6
    gps_unix_diff_millis = 315964782000
    utc_time_millis = gps_time_millis + gps_unix_diff_millis
    return str(utc_time_millis)


def raw_recalculate_time_to_ms(location="Staadion", device="Pixel", date="21_04"):
    output_filename = f"{device}_{date}_{location}.txt"

    # Get the current file location
    current_script_path = os.path.realpath(__file__)

    # Get the base directory
    base_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

    output_directory = os.path.join(base_directory, "output", f"{date}")

    os.makedirs(output_directory, exist_ok=True)
    output_file_path = os.path.join(output_directory, output_filename)

    with open(output_file_path, 'w', newline='') as f:

        # Set the default input folder
        input_directory = os.path.join(base_directory, 'input', date)

        input_path = Path(input_directory)

        # Find the first file
        input_file_path = [file for file in input_path.iterdir() if file.is_file() and file.suffix == ".txt"][0]

        with open(input_file_path, 'r') as stream:
            for line in stream:
                # split line into list of items
                items = line.strip().split(',')

                # check if the first item is "Raw"
                if items[0] == "Raw":
                    # perform the calculation and overwrite the value at index 1
                    gps_time = float(items[2]) - (float(items[5]) + float(items[6]))
                    items[1] = gpst_to_utc(gps_time)

                # join the items back together and write the line to the output file
                f.write(','.join(items) + '\n')


if __name__ == "__main__":
    raw_recalculate_time_to_ms()