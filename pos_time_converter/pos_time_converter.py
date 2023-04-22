import csv
import os
import datetime

# Constants (choose one that fits for you or make your own)
locations = ["Staadion", "Tudengimaja"]
devices = ["Pixel", "Xiaomi"]

date = "22_04"
device = devices[1]
location = locations[1]


input_filename = f"{date}/{device}_{date}_{location}_pos"

output_directory = f"output/{date}/"
output_filename = f"{device}_pos_{date}_{location}.csv"

def convertTime():
    os.makedirs(os.path.dirname(f"{output_directory}/{output_filename}"), exist_ok=True)

    with open(f"{output_directory}/{output_filename}", 'w', newline='') as f:
        writer = csv.writer(f)

        header = ["Time", "Latitude", "Longitude"]
        writer.writerow(header)

        stream = open(fr'input/{input_filename}.pos', 'r')
        for line in stream:
            if line[0].isdigit():
                lineList = line.split("   ")
                gpsTime = lineList[0]
                time = getTimeFromGPST(gpsTime)
                latitude = lineList[1]
                longitude = lineList[2]
                row = [time, latitude, longitude]
                writer.writerow(row)

def getTimeFromGPST(gpst: str) -> str:
    splitedGPST = gpst.split(" ")
    weeks = int(splitedGPST[0])
    seconds = int(splitedGPST[1][:-4])
    # Constants from the formula
    minus_seconds = 18

    # Calculate the new date
    new_date = datetime.datetime(1980, 1, 6) + datetime.timedelta(weeks=weeks, seconds=(seconds - minus_seconds))
    formatted_result = new_date.strftime("%H:%M:%S")
    print(formatted_result)
    return formatted_result

if __name__ == "__main__":
    convertTime()
