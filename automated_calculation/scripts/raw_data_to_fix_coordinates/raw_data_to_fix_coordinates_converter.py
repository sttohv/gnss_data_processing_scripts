import csv
import datetime
import os
import statistics

FIX_DATA_TYPE = "Fix"
RAW_DATA_TYPE = "Raw"

# ToDo these might have to be renamed to sth more descriptive
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

# Constants (choose one that fits for you or make your own)
# calculating determines if whole function (True) or just this file (False)
# NOTE both False and True work for calculating
# ToDo provider here doesnt mean constellation but rather fix type (GPS, NLP, FLP). Login in main.py should be changed
def convert_raw_data_to_fix_coordinates(location="Tudengimaja", device="Pixel", date="22_04", provider="GPS", calculating=False):
    output_filename = f"{device}_{FIX_DATA_TYPE}_{provider}_{date}_{location}.csv"
    input_filename = f"{device}_{date}_{location}"

    # Get the current file location
    current_script_path = os.path.realpath(__file__)

    # Get the base directory
    base_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

    if calculating:
        output_directory = os.path.join(base_directory, "output", f"{date}")
    else:
        output_directory = os.path.join(base_directory, 'scripts', 'raw_data_to_fix_coordinates', "intermediate_results", f"{date}")

    os.makedirs(output_directory, exist_ok=True)
    output_file_path = os.path.join(output_directory, output_filename)

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

        # Change file name if needed
        if calculating:
            input_directory = os.path.join(base_directory, 'input')
        else:
            input_directory = os.path.join(base_directory, 'scripts', 'raw_data_to_fix_coordinates', 'input', f"{date}")

        input_file_path = os.path.join(input_directory, f'{input_filename}.txt')

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

            # ToDo separate function for parsing Fix data?
            if line_data_type == FIX_DATA_TYPE:
                line_provider = line_list[1]

                if line_provider == provider:
                    if current_fix_time == current_raw_time: # and sum(galileo_single_freq_satellite_counter,galileo_dual_freq_satellite_counter, GPS_single_freq_satellite_counter,GPS_dual_freq_satellite_counter)
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

                        # # Reset counters until next Fix is found
                        # galileo_single_freq_satellite_counter = 0
                        # GPS_single_freq_satellite_counter = 0
                        # galileo_dual_freq_satellite_counter = 0
                        # GPS_dual_freq_satellite_counter = 0

                    # Start of a new epoch
                    current_fix_time = line_list[8][:-3]
                    fix_latitude = line_list[2]
                    fix_longitude = line_list[3]
                    fix_converted_time = convert_unix_time_millis_to_time(int(line_list[8]))

            # ToDo separate function for parsing Raw data?
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

# Pythoni indeksid
# Frequency = 22
# ConstellationType = 28
# SVID = 11
# Cn0DbHz = 16
# PseudorangeRateMetersPerSecond = 17


# time,rover_latitude,rover_longitude,ground_truth_latitude,ground_truth_longitude,distance_from_last_coord,deviation, galileo_L1_total, galileo_L5_total, GPS_L1_total, GPS_L5_total


if __name__ == "__main__":
    convert_raw_data_to_fix_coordinates()
