import csv
import os
import datetime


# Constants (choose one that fits for you or make your own)
# calculating determines if whole function (True) or just this file (False)
# NOTE both False and True work for calculating
def convert_GPST_to_time(location="Tudengimaja", device="Pixel", date="22_04", calculating=True):
    output_filename = f"{device}_pos_{date}_{location}.csv"
    input_filename = f"{device}_{date}_{location}_pos"

    # Get the current file location
    current_script_path = os.path.realpath(__file__)

    # Get the base directory
    base_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

    # Individual procedure
    if calculating:
        output_directory = os.path.join(base_directory, "output", f"{date}")
        # os.makedirs(os.path.dirname(f"{output_directory}/{output_filename}"), exist_ok=True)
    else:
        output_directory = os.path.join(base_directory, 'scripts', 'pos_time_converter', "output", f"{date}")
        # os.makedirs(os.path.dirname(f"{output_directory}/{output_filename}"), exist_ok=True)

    os.makedirs(output_directory, exist_ok=True)
    output_file_path = os.path.join(output_directory, output_filename)

    with open(output_file_path, 'w', newline='') as f:
        writer = csv.writer(f)

        header = ["time", "latitude", "longitude"]
        writer.writerow(header)

        if calculating:
            input_directory = os.path.join(base_directory, 'input')
        else:
            input_directory = os.path.join(base_directory, 'scripts', 'pos_time_converter', 'input', f"{date}")

        input_file_path = os.path.join(input_directory, f'{input_filename}.pos')

        stream = open(input_file_path, 'r')
        for line in stream:
            if line[0].isdigit():
                lineList = line.split("   ")
                gpsTime = lineList[0]
                time = get_time_from_GPST(gpsTime)
                latitude = lineList[1]
                longitude = lineList[2].split()[0]
                row = [time, latitude, longitude]
                writer.writerow(row)

def get_time_from_GPST(gpst: str) -> str:
    splitedGPST = gpst.split(" ")
    weeks = int(splitedGPST[0])
    seconds = int(splitedGPST[1][:-4])
    # Constants from the formula
    minus_seconds = 18

    # Calculate the new date
    new_date = datetime.datetime(1980, 1, 6) + datetime.timedelta(weeks=weeks, seconds=(seconds - minus_seconds))
    formatted_result = new_date.strftime("%H:%M:%S")
    return formatted_result

if __name__ == "__main__":
    convert_GPST_to_time()
