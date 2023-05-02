import csv
import datetime
import os

data_type = "Fix"

def convert_unix_time_millis_to_time(unix_time_millis: int):
    unix_time_seconds = unix_time_millis / 1000

    # Convert to datetime object in UTC
    datetime_obj_utc = datetime.datetime.utcfromtimestamp(unix_time_seconds)

    # Format as "hh:mm:ss"
    formatted_time = datetime_obj_utc.strftime("%H:%M:%S")

    return formatted_time

# Constants (choose one that fits for you or make your own)
# calculating determines if whole function (True) or just this file (False)
# NOTE both False and True work for calculating
def convert_raw_data_to_fix_coordinates(location="Tudengimaja", device="Pixel", date="22_04", provider="GPS", calculating=False):
    output_filename = f"{device}_{data_type}{provider}_{date}_{location}.csv"
    input_filename = f"{device}_{date}_{location}"

    # Get the current file location
    current_script_path = os.path.realpath(__file__)

    # Get the base directory
    base_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

    if calculating:
        output_directory = os.path.join(base_directory, "output", f"{date}")
    else:
        output_directory = os.path.join(base_directory, 'scripts', 'raw_data_to_fix_coordinates', "output", f"{date}")

    os.makedirs(output_directory, exist_ok=True)
    output_file_path = os.path.join(output_directory, output_filename)

    with open(output_file_path, 'w', newline='') as f:
        writer = csv.writer(f)

        header = ["time", "latitude", "longitude"]
        writer.writerow(header)

        # Change file name if needed
        if calculating:
            input_directory = os.path.join(base_directory, 'input')
        else:
            input_directory = os.path.join(base_directory, 'scripts', 'raw_data_to_fix_coordinates', 'input', f"{date}")

        input_file_path = os.path.join(input_directory, f'{input_filename}.txt')

        stream = open(input_file_path, 'r')
        for line in stream:
            lineList = line.split(",")
            line_data_type = lineList[0]
            if line_data_type == data_type:
                line_provider = lineList[1]
                # ToDo provider needs to be changed because it only works with GPS atm
                if line_provider == provider:
                    latitude = lineList[2]
                    longitude = lineList[3]
                    time = convert_unix_time_millis_to_time(int(lineList[8]))
                    row = [time, latitude, longitude]
                    writer.writerow(row)

if __name__ == "__main__":
    convert_raw_data_to_fix_coordinates()
