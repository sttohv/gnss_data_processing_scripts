import csv
import os
from pyubx2 import UBXReader
from pynmeagps import NMEAMessage

locations = ["Staadion", "Tudengimaja"]

file_type = "Referentsandmed"
location = locations[1]
date = "22_04"

input_filename = f"{file_type}_{date}_{location}"

output_filename = f"{file_type}_{date}_{location}.csv"
output_directory = f"output/{date}/"

os.makedirs(os.path.dirname(f"{output_directory}/{output_filename}"), exist_ok=True)

with open(f"{output_directory}/{output_filename}", 'w', newline='') as f:
    writer = csv.writer(f)

    header = ["time", "latitude", "longitude"]
    writer.writerow(header)

    # Change file name if needed
    stream = open(fr'input/{input_filename}.ubx', 'rb')
    ubr = UBXReader(stream)

    for (raw_data, parsed_data) in ubr:
        if isinstance(parsed_data, NMEAMessage):
            if parsed_data.identity == 'GNRMC':
                row = [parsed_data.__dict__.get('time'), parsed_data.__dict__.get('lat'), parsed_data.__dict__.get('lon')]
                writer.writerow(row)

# Kas siit saab kätte, mis tüüpi FIXiga on tegu?