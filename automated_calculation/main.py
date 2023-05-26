import csv
import os
import yaml

from automated_calculation.scripts.pos_time_converter.pos_time_converter import convert_GPST_to_time
from automated_calculation.scripts.raw_data_to_fix_coordinates.raw_data_to_fix_coordinates_converter import \
    convert_raw_data_to_fix_coordinates
from automated_calculation.scripts.standard_deviation_and_mean_calculator.standard_deviation_and_mean_calculator import \
    main
from automated_calculation.scripts.ubx_to_coordinates_converter.ubx_to_coordinates_converter import convert_ubx_to_csv


def read_configuration():
    with open('configuration.yaml') as file:
        config = yaml.safe_load(file)

    location = config['location']
    date = config['date']
    device = config['device']
    ubx_conversion = config['ubx_conversion']
    raw_data_conversion = config['raw_data_conversion']
    pos_conversion = config['pos_conversion']
    systematic_error = config['systematic_error']
    provider = config['provider']
    constellations = config["constellations"]
    epsilon = config['epsilon']

    return location, date, device, ubx_conversion, raw_data_conversion, pos_conversion, systematic_error, provider, constellations, epsilon


# Do conversions and save results to output folder
def convert_input_data(location, date, device, ubx_conversion, raw_data_conversion, pos_conversion, provider):
    success_counter = 0
    if ubx_conversion:
        convert_ubx_to_csv(location, date)
        print("ubx converted successfully")
        success_counter += 1
    if raw_data_conversion:
        convert_raw_data_to_fix_coordinates(location, device, date, provider)
        print("raw converted successfully")
        success_counter += 1
    if pos_conversion:
        convert_GPST_to_time(location, device, date)
        print("processed converted successfully")
        success_counter += 1

    return success_counter

def write_report_about_measurement(location, date, device, constellations):
    # Get the current file location
    current_script_path = os.path.realpath(__file__)

    # Get the base directory
    base_directory = os.path.dirname(current_script_path)

    # Set the output folder and file name
    output_folder = os.path.join(base_directory, "output", date)
    output_file_name = f"Results_{constellations}_{device}_{date}_{location}.csv"

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Construct the output file path
    output_file_path = os.path.join(output_folder, output_file_name)

    with open(output_file_path, 'w', newline='') as f:
        writer = csv.writer(f)

        header = ["Data", constellations]
        writer.writerow(header)
        row_1 = ["Raw data and ground truth mean error", raw_mean_deviation]
        writer.writerow(row_1)
        row_2 = ["Processed data and ground truth mean error", processed_mean_deviation]
        writer.writerow(row_2)
        row_3 = ["Raw and processed data mean error difference", subtraction_of_raw_and_processed_mean_deviation]
        writer.writerow(row_3)
        row_4 = ["Raw data and ground truth standard deviation", raw_standard_deviation]
        writer.writerow(row_4)
        row_5 = ["Processed data and ground truth standard deviation", processed_standard_deviation]
        writer.writerow(row_5)
        row_6 = ["Raw and processed data standard deviation difference", difference_of_raw_and_processed_standard_deviation]
        writer.writerow(row_6)

    print(f"results can be seen in output/{date}")

if __name__ == "__main__":
    LOCATION, DATE, DEVICE, UBX_CONVERSION, RAW_DATA_CONVERSION, POS_CONVERSION, SYSTEMATIC_ERROR, PROVIDER, CONSTELLATIONS, EPSILON = read_configuration()
    success_counter = convert_input_data(LOCATION, DATE, DEVICE, UBX_CONVERSION, RAW_DATA_CONVERSION, POS_CONVERSION, PROVIDER)
    if success_counter == 3:
        raw_mean_deviation, processed_mean_deviation, raw_standard_deviation, processed_standard_deviation, subtraction_of_raw_and_processed_mean_deviation, difference_of_raw_and_processed_standard_deviation = main(
            DATE, SYSTEMATIC_ERROR, EPSILON, DEVICE, LOCATION)
        write_report_about_measurement(LOCATION, DATE, DEVICE, CONSTELLATIONS)