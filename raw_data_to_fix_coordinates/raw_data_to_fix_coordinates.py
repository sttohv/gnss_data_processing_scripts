import csv
import os

provider = "GPS"
date = "22_04"
location = "tudengimaja"
device = "Pixel"

data_type = "Fix"

input_filename = f"{date}/{device}_{date}_{location}"

output_directory = f"output/{date}/"
output_filename = f"{device}_{data_type}{provider}_{date}_{location}.csv"

os.makedirs(os.path.dirname(f"{output_directory}/{output_filename}"), exist_ok=True)

with open(f"{output_directory}/{output_filename}", 'w', newline='') as f:
    writer = csv.writer(f)

    header = ["Fix", "Provider", "LatitudeDegrees", "LongitudeDegrees", "UnixTimeMillis"]
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
                time = lineList[8]
                row = [line_data_type, line_provider, latitude, longitude, time]
                writer.writerow(row)