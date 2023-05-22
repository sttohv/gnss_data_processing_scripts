import csv
import os
from pyubx2 import UBXReader, UBXMessage
from pynmeagps import NMEAMessage

file_type = "Referentsandmed"

# NOTE both False and True work for calculating
def convert_ubx_to_csv(location="Test", date="07_05", calculating=False):
    output_filename = f"{file_type}_{date}_{location}.csv"
    input_filename = f"{file_type}_{date}_{location}"

    # Get the current file location
    current_script_path = os.path.realpath(__file__)

    # Get the base directory
    base_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

    if calculating:
        output_directory = os.path.join(base_directory, "intermediate_results", f"{date}")
    else:
        output_directory = os.path.join(base_directory, 'scripts', 'ubx_to_coordinates_converter', "output", f"{date}")

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
            input_directory = os.path.join(base_directory, 'scripts', 'ubx_to_coordinates_converter', 'input')

        input_file_path = os.path.join(input_directory, f'{input_filename}.ubx')

        stream = open(input_file_path, 'rb')
        ubr = UBXReader(stream)

        for (raw_data, parsed_data) in ubr:
            if isinstance(parsed_data, NMEAMessage):
                if parsed_data.identity == 'GNRMC':
                    row = [parsed_data.__dict__.get('time'), parsed_data.__dict__.get('lat'), parsed_data.__dict__.get('lon')]
                    # print(parsed_data.__dict__)
                    writer.writerow(row)
        #         # UBX - ESF - MEAS
        #         # if parsed_data.identity == 'UBX-ESF-MEAS':


        # ToDo needed for future development
        # for (raw_data, parsed_data) in ubr:
        #     if isinstance(parsed_data, UBXMessage):
        #         if parsed_data.identity == "NAV-PVT":
        #             time_utc = f"{parsed_data.hour:02d}:{parsed_data.min:02d}:{parsed_data.second:02d}.{parsed_data.nano // 10:03d}"
        #             latitude = parsed_data.lat
        #             longitude = parsed_data.lon
        #             print(time_utc)
        #         if parsed_data.identity == 'ESF-MEAS':
        #             print(parsed_data)
        #             direction_vector = 0
        #         # if time_utc and latitude and longitude and direction_vector:
        #         #     row = [time_utc, latitude, longitude, direction_vector]
        #         #     writer.writerow(row)
        #         #     # May be obselete
        #         #     time_utc, latitude, longitude, direction_vector = None, None, None, None

if __name__ == "__main__":
    convert_ubx_to_csv()
