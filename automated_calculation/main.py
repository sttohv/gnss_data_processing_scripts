import csv
import os

from automated_calculation.scripts.deviation_and_mean_calculator.deviation_and_mean_calculator import main
from automated_calculation.scripts.pos_time_converter.pos_time_converter import convert_GPST_to_time
from automated_calculation.scripts.raw_data_to_fix_coordinates.raw_data_to_fix_coordinates_converter import \
    convert_raw_data_to_fix_coordinates
from automated_calculation.scripts.ubx_to_coordinates_converter.ubx_to_coordinates_converter import convert_ubx_to_csv

# Input parameters
locations = ["Staadion", "Tudengimaja"]
date = "22_04"
devices = ["Pixel", "Xiaomi"]
constellations = ["GPS", "GLONASS", "Galileo", "ALL"]
parts = ["ALL", "Ring1", "Ring2", "Ring3", "Ring4", "Custom"]

configuration = [locations[1], date, devices[0], constellations[0], "new_" + parts[5]]


# Do conversions and save results to output folder
def convert_input_data():
    # pass
    # convert_ubx_to_csv(configuration[0], configuration[1], True)
    # convert_raw_data_to_fix_coordinates(configuration[0], configuration[2], configuration[1], configuration[3], True)
    convert_GPST_to_time(configuration[0], configuration[2], configuration[1], True)

def write_report_about_measurement():
    # Get the current file location
    current_script_path = os.path.realpath(__file__)

    # Get the base directory
    base_directory = os.path.dirname(current_script_path)

    # Set the output folder and file name
    output_folder = os.path.join(base_directory, "calculation_results")
    output_file_name = f"Results_{configuration[4]}_{configuration[2]}_{configuration[1]}_{configuration[0]}.csv"

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Construct the output file path
    output_file_path = os.path.join(output_folder, output_file_name)

    with open(output_file_path, 'w', newline='') as f:
        writer = csv.writer(f)

        header = ["Andmed", constellations[0]]
        writer.writerow(header)
        row_1 = ["Toorandmete ja referentsandmete keskmine viga", raw_mean_deviation]
        writer.writerow(row_1)
        row_2 = ["Järeltöötlus andmete ja referentsandmete keskmine viga", processed_mean_deviation]
        writer.writerow(row_2)
        row_3 = ["Toorandmete ja järeltöötluse keskmise vea vahe", subtraction_of_raw_and_processed_mean_deviation]
        writer.writerow(row_3)
        row_4 = ["Toorandmete ja referentsandmete standardhälve", raw_standard_deviation]
        writer.writerow(row_4)
        row_5 = ["Järeltöötlus andmete ja referentsandmete standardhälve", processed_standard_deviation]
        writer.writerow(row_5)
        row_6 = ["Toorandmete ja järeltöötluse standardhälve vahe", subtraction_of_raw_and_processed_standard_deviation]
        writer.writerow(row_6)

if __name__ == "__main__":
    convert_input_data()
    raw_mean_deviation, processed_mean_deviation, raw_standard_deviation, processed_standard_deviation, subtraction_of_raw_and_processed_mean_deviation, subtraction_of_raw_and_processed_standard_deviation = main(
        date)
    write_report_about_measurement()

# ToDo Below
# Make sure every method makes output folder. main.py should make an input folder (or write in README that one should be made manually). or user can upload files
# main.py function should be polished. It works but it is kinda ugly
# add functionality to make directories automatically to automated_calculation