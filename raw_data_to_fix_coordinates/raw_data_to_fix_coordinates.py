import csv

filename = "Staadion_18.04_xiaomi"
FILE_TYPE = "Fix-GPS"
location = "Staadion"
date = "18_04_2023"

with open(f"output/[{FILE_TYPE}][{date}][{location}].csv", 'w', newline='') as f:
    writer = csv.writer(f)

    header = ["Fix","Provider","LatitudeDegrees","LongitudeDegrees","UnixTimeMillis"]
    writer.writerow(header)

    stream = open(fr'input/{filename}.txt', 'r')
    for line in stream:
        lineList = line.split(",")
        dataType = lineList[0]
        if(dataType == "Fix"):
            provider = lineList[1]
            if(provider == "GPS"):
                latitude = lineList[2]
                longitude = lineList[3]
                time = lineList[8]
                row = [dataType, provider,latitude, longitude, time]
                writer.writerow(row)