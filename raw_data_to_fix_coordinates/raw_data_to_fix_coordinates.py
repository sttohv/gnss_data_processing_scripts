import csv


provider = "GPS"
date = "22_04"
location = "tudengimaja"
device = "Xiaomi"

input_filename = f"{date}/{device}_{date}_{location}"

# Don't edit next one
data_type = "Fix"

with open(f"output/{date}/{device}_{data_type}{provider}_{date}_{location}.csv", 'w', newline='') as f:
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