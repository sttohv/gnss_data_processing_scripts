import csv

input_filename = "Staadion_18.04_xiaomi"
provider = "GPS"
date = "18_04_2023"
location = "Staadion"

# Don't edit next one
data_type = "Fix"

with open(f"output/[{data_type}{provider}][{date}][{location}].csv", 'w', newline='') as f:
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