import csv
from pyubx2 import UBXReader
from pynmeagps import NMEAMessage


FILE_TYPE = "UUS_Tõeandmed"
location = "Tudengimaja"
date = "18.04.2023"

with open(f"output/[{FILE_TYPE}][{date}][{location}].csv", 'w', newline='') as f:
    writer = csv.writer(f)

    header = ["time", "latitude", "longitude"]
    writer.writerow(header)

    # Change file name if needed
    stream = open(r'input/UUS_Tõeandmed_18.04_Tudengimaja.ubx', 'rb')
    ubr = UBXReader(stream)

    for (raw_data, parsed_data) in ubr:
        if isinstance(parsed_data, NMEAMessage):
            if parsed_data.identity == 'GNRMC':
                row = [parsed_data.__dict__.get('time'), parsed_data.__dict__.get('lat'), parsed_data.__dict__.get('lon')]
                writer.writerow(row)

# Kas siit saab kätte, mis tüüpi FIXiga on tegu?


