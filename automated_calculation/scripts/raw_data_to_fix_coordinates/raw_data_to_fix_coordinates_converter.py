import csv
import datetime
import os
import statistics
from pathlib import Path

FIX_DATA_TYPE = "Fix"
RAW_DATA_TYPE = "Raw"

SINGLE_FREQUENCY_BANDWIDTH = "1575420030"
DUAL_FREQUENCY_BANDWIDTH = "1176450050"
GALILEO_CONSTELLATION_TYPE = "6"
GPS_CONSTELLATION_TYPE = "1"


def convert_unix_time_millis_to_time(unix_time_millis: int):
    unix_time_seconds = unix_time_millis / 1000

    # Convert to datetime object in UTC
    datetime_obj_utc = datetime.datetime.utcfromtimestamp(unix_time_seconds)

    # Format as "hh:mm:ss.sss"
    formatted_time = datetime_obj_utc.strftime("%H:%M:%S")

    return formatted_time


def convert_raw_data_to_fix_coordinates(location="Staadion", device="Pixel", date="13_05", provider="GPS"):
    filepaths = get_files(date, device, location, provider)

    output_file_path = filepaths[0]
    input_file_path = filepaths[1]

    with open(output_file_path, 'w', newline='') as f:
        writer = csv.writer(f)

        header = ["time",
                  "latitude",
                  "longitude",
                  "num_of_galileo_E1_freq_satellites",
                  "num_of_galileo_E5_freq_satellites",
                  "num_of_GPS_L1_freq_satellites",
                  "num_of_GPS_L5_freq_satellites",
                  "Cn0DbHz_epoch_average",
                  "pseudorange_rate_meters_per_second_epoch_average"
                  ]
        writer.writerow(header)

        stream = open(input_file_path, 'r')

        galileo_single_freq_satellite_counter = 0
        GPS_single_freq_satellite_counter = 0
        galileo_dual_freq_satellite_counter = 0
        GPS_dual_freq_satellite_counter = 0
        Cn0DbHz_counter = []
        pseudorange_rate_meters_per_second_counter = []

        previous_raw_time = -1
        current_raw_time = -1
        current_fix_time = 0
        fix_longitude = 0
        fix_latitude = 0
        fix_converted_time = 0

        for line in stream:
            line_list = line.split(",")
            line_data_type = line_list[0]

            if line_data_type == FIX_DATA_TYPE:
                line_provider = line_list[1]

                if line_provider == provider:
                    if current_fix_time == current_raw_time:
                        fix_row = [fix_converted_time,
                                   fix_latitude,
                                   fix_longitude,
                                   galileo_single_freq_satellite_counter,
                                   galileo_dual_freq_satellite_counter,
                                   GPS_single_freq_satellite_counter,
                                   GPS_dual_freq_satellite_counter,
                                   statistics.fmean(Cn0DbHz_counter),
                                   statistics.fmean(pseudorange_rate_meters_per_second_counter)
                                   ]
                        writer.writerow(fix_row)
                    # Start of a new epoch
                    current_fix_time = line_list[8][:-3]
                    fix_latitude = line_list[2]
                    fix_longitude = line_list[3]
                    fix_converted_time = convert_unix_time_millis_to_time(int(line_list[8]))

            elif line_data_type == RAW_DATA_TYPE and current_fix_time != 0:
                frequency = line_list[22]
                constellation_type = line_list[28]

                current_raw_time = line_list[1][:-3]

                if previous_raw_time != current_raw_time:
                    # Reset if a new epoch has started
                    galileo_single_freq_satellite_counter = 0
                    GPS_single_freq_satellite_counter = 0
                    galileo_dual_freq_satellite_counter = 0
                    GPS_dual_freq_satellite_counter = 0
                    Cn0DbHz_counter = []
                    pseudorange_rate_meters_per_second_counter = []

                Cn0DbHz_counter.append(float(line_list[16]))
                pseudorange_rate_meters_per_second_counter.append(float(line_list[17]))

                if frequency == SINGLE_FREQUENCY_BANDWIDTH:
                    if constellation_type == GALILEO_CONSTELLATION_TYPE:
                        galileo_single_freq_satellite_counter += 1
                    if constellation_type == GPS_CONSTELLATION_TYPE:
                        GPS_single_freq_satellite_counter += 1
                elif frequency == DUAL_FREQUENCY_BANDWIDTH:
                    if constellation_type == GALILEO_CONSTELLATION_TYPE:
                        galileo_dual_freq_satellite_counter += 1
                    if constellation_type == GPS_CONSTELLATION_TYPE:
                        GPS_dual_freq_satellite_counter += 1

                previous_raw_time = line_list[1][:-3]

def get_files(date, device, location, provider):
    # Get the current file location
    current_script_path = os.path.realpath(__file__)
    # Get the base directory
    base_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

    # Set input and output directories
    input_directory = os.path.join(base_directory, "input", date)
    output_directory = os.path.join(base_directory, "output", f"{date}")

    input_path = Path(input_directory)
    input_file_names = [file.name for file in input_path.iterdir() if file.is_file() and file.suffix == ".txt"]
    input_filename = input_file_names[0]
    output_filename = f"{device}_{FIX_DATA_TYPE}_{provider}_{date}_{location}.csv"

    os.makedirs(output_directory, exist_ok=True)
    output_file_path = os.path.join(output_directory, output_filename)
    input_file_path = os.path.join(input_directory, input_filename)
    return output_file_path, input_file_path

if __name__ == "__main__":
    convert_raw_data_to_fix_coordinates()
