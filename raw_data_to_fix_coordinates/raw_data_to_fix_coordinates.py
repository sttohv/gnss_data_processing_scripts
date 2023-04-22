import csv
import datetime
import os

import pytz

# Constants (choose one that fits for you or make your own)
locations = ["Staadion", "Tudengimaja"]
devices = ["Pixel", "Xiaomi"]

provider = "GPS"
date = "22_04"
data_type = "Fix"
device = devices[1]
location = locations[1]


input_filename = f"{date}/{device}_{date}_{location}"

output_directory = f"output/{date}/"
output_filename = f"{device}_{data_type}{provider}_{date}_{location}.csv"

os.makedirs(os.path.dirname(f"{output_directory}/{output_filename}"), exist_ok=True)

def convert_unix_time_millis_to_time(unix_time_millis: int):
    unix_time_seconds = unix_time_millis / 1000

    # Convert to datetime object in UTC
    datetime_obj_utc = datetime.datetime.utcfromtimestamp(unix_time_seconds)

    # Format as "hh:mm:ss"
    formatted_time = datetime_obj_utc.strftime("%H:%M:%S")

    return formatted_time

with open(f"{output_directory}/{output_filename}", 'w', newline='') as f:
    writer = csv.writer(f)

    header = ["fix", "provider", "latitude", "longitude", "time"]
    writer.writerow(header)

    stream = open(fr'input/{input_filename}.txt', 'r')
    for line in stream:
        lineList = line.split(",")
        line_data_type = lineList[0]
        if line_data_type == data_type:
            line_provider = lineList[1]
            if line_provider == provider:
                latitude = lineList[2]
                longitude = lineList[3]
                time = convert_unix_time_millis_to_time(int(lineList[8]))
                row = [line_data_type, line_provider, latitude, longitude, time]
                writer.writerow(row)