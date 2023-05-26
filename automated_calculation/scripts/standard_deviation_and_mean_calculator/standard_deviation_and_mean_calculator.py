import math
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from pandas import read_csv
from coordinates.converter import CoordinateConverter, WGS84, L_Est97

converter = CoordinateConverter()

# Read the files in (needs to be changed according to file)
def read_data_files(date):
    # Get the current file location
    current_script_path = os.path.realpath(__file__)
    # Get the base directory
    base_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

    input_directory = os.path.join(base_directory, "output", date)
    input_path = Path(input_directory)

    file_names = [file.name for file in input_path.iterdir() if file.is_file() and file.suffix == ".csv"]

    raw_rover_data_file = [file_name for file_name in file_names if "Fix" in file_name][0]
    processed_rover_data_file = [file_name for file_name in file_names if "pos" in file_name][0]
    ground_truth_data_file = [file_name for file_name in file_names if "Referentsandmed" in file_name][0]

    raw_rover_file = input_path / raw_rover_data_file
    processed_rover_file = input_path / processed_rover_data_file
    ground_truth_file = input_path / ground_truth_data_file

    raw_rover = read_csv(raw_rover_file, delimiter=",")
    processed_rover = read_csv(processed_rover_file, delimiter=",")
    ground_truth = read_csv(ground_truth_file, delimiter=",")

    # Convert 'time' column to pandas.Timestamp
    raw_rover = convert_time_column(raw_rover)
    processed_rover = convert_time_column(processed_rover)
    ground_truth = convert_time_column(ground_truth)

    return raw_rover, processed_rover, ground_truth


def convert_time_column(dataframe, time_format="%H:%M:%S"):
    dataframe['time'] = pd.to_datetime(dataframe['time'], format=time_format)
    return dataframe


def merge_dataframes(raw_rover, processed_rover, ground_truth):
    processed_merged = pd.merge(processed_rover, ground_truth, on="time")
    raw_merged = pd.merge(raw_rover, ground_truth, on="time")

    processed_merged = processed_merged.rename(columns={'latitude_x': 'rover_latitude',
                                                        'longitude_x': 'rover_longitude',
                                                        'latitude_y': 'ground_truth_latitude',
                                                        'longitude_y': 'ground_truth_longitude'})

    raw_merged = raw_merged.rename(columns={'latitude_x': 'rover_latitude',
                                            'longitude_x': 'rover_longitude',
                                            'latitude_y': 'ground_truth_latitude',
                                            'longitude_y': 'ground_truth_longitude'})

    return processed_merged, raw_merged


def replace_WGS84_with_LEST97(dataframe):
    new_latitude_values = []
    new_longitude_values = []

    for index, row in dataframe.iterrows():
        # Converting rover coordinates to LEST97
        coord_wgs84 = WGS84(lat=row['latitude'], long=row['longitude'])
        coord_lest97 = converter.wgs84_to_l_est97(coord_wgs84)

        # Append the new L-Est97 latitude value to the list
        new_latitude_values.append(coord_lest97.x)
        new_longitude_values.append(coord_lest97.y)

    # Overwrite the latitude and longitude column in the dataframe with the new L-Est97 values
    dataframe['latitude'] = new_latitude_values
    dataframe['longitude'] = new_longitude_values

    return dataframe


def remove_systematic_error_from_dataframe(merged_dataframe, systematic_error):
    result_dataframe = merged_dataframe.copy()
    for index, row in result_dataframe.iterrows():
        if index == 0:
            continue

        previous_row = merged_dataframe.iloc[index - 1]
        current_coord = L_Est97(row["ground_truth_latitude"], row["ground_truth_longitude"])
        previous_coord = L_Est97(previous_row["ground_truth_latitude"], previous_row["ground_truth_longitude"])

        # Calculate length of direction vector between previous and current
        direction_vector = calculate_direction_vector(current_coord, previous_coord)

        # Add direction vector coordinates to dataframe
        row["direction_vector_x"] = direction_vector.x
        row["direction_vector_y"] = direction_vector.y

        # Calculate length of direction vector
        direction_vector_length = math.sqrt(direction_vector.x ** 2 + direction_vector.y ** 2)

        # Normalize direction vector
        normalized_direction_vector = normalize_direction_vector(direction_vector, direction_vector_length)

        # Check if direction_vector was normalized correctly
        sqrt = math.sqrt(normalized_direction_vector.x ** 2 + normalized_direction_vector.y ** 2)
        if sqrt <= 1 and sqrt > 0.99999999:
            row["normalized_correctly"] = True
        else:
            # Can be potential error
            row["normalized_correctly"] = False
            continue

        # Calculate new rover coordinate
        current_rover_coordinate = L_Est97(row["rover_latitude"], row["rover_longitude"])
        new_rover_coordinate = calculate_new_rover_coordinate(normalized_direction_vector, current_rover_coordinate,
                                                              systematic_error)

        result_dataframe.at[index, "rover_latitude"] = new_rover_coordinate.x
        result_dataframe.at[index, "rover_longitude"] = new_rover_coordinate.y

    return result_dataframe


def calculate_direction_vector(current_coord, previous_coord):
    return L_Est97(current_coord.x - previous_coord.x, current_coord.y - previous_coord.y)


def normalize_direction_vector(direction_vector, direction_length_vector):
    return L_Est97(direction_vector.x / direction_length_vector, direction_vector.y / direction_length_vector)


def calculate_new_rover_coordinate(normalised_direction_vector, current_rover_coordinate, distance_error):
    return L_Est97(current_rover_coordinate.x - distance_error * normalised_direction_vector.x,
                    current_rover_coordinate.y - distance_error * normalised_direction_vector.y)


def calculate_deviation(deviation, row):
    # Incrementing deviation
    rover_coord_lest97 = L_Est97(row["rover_latitude"], row["rover_longitude"])
    ground_truth_coord_lest97 = L_Est97(row["ground_truth_latitude"], row["ground_truth_longitude"])
    deviation += calculate_euclidean_distance(rover_coord_lest97, ground_truth_coord_lest97)
    return deviation


def draw_coordinates_and_their_connection(rover_coord_lest97, ground_truth_coord_lest97, line_color, truth_color,
                                          rover_color, min_x, min_y):
    # Plotting
    plt.plot([rover_coord_lest97.x - min_x, ground_truth_coord_lest97.x - min_x],
             [rover_coord_lest97.y - min_y, ground_truth_coord_lest97.y - min_y], line_color, markersize=1)
    plt.plot([ground_truth_coord_lest97.x - min_x], [ground_truth_coord_lest97.y - min_y], truth_color, markersize=1.2)
    plt.plot([rover_coord_lest97.x - min_x], [rover_coord_lest97.y - min_y], rover_color, markersize=1.2)


def calculate_euclidean_distance(coord1: L_Est97, coord2: L_Est97):
    return math.sqrt((coord1.x - coord2.x) ** 2 + (coord1.y - coord2.y) ** 2)


# Duplicate function. probably better than mine
def wgs84_to_lest97_coordinates(latitudes, longitudes):
    coordinates_wgs84 = np.column_stack((latitudes, longitudes))
    return [converter.wgs84_to_l_est97(WGS84(lat=lat, long=long)) for lat, long in coordinates_wgs84]


def find_min_lest97_coordinates(dataframe):
    latitudes = dataframe['rover_latitude'].to_numpy()
    longitudes = dataframe['rover_latitude'].to_numpy()
    coordinates_lest97 = wgs84_to_lest97_coordinates(latitudes, longitudes)
    return min(coord.x for coord in coordinates_lest97) - 10, min(coord.y for coord in coordinates_lest97) - 10


def calculate_standard_deviation(distances):
    mean_distance = np.mean(distances)
    squared_diff = [(d - mean_distance) ** 2 for d in distances]
    variance = np.mean(squared_diff)
    standard_deviation = np.sqrt(variance)
    return standard_deviation


def add_ground_truth_euclidean(dataframe, epsilon):
    for index, row in dataframe.iterrows():
        if index == 0:
            continue

        previous_row = dataframe.iloc[index - 1]

        current_coord = L_Est97(row["latitude"], row["longitude"])
        previous_coord = L_Est97(previous_row["latitude"], previous_row["longitude"])

        euclidean_distance_between_coords = calculate_euclidean_distance(current_coord, previous_coord)

        # Ternary conditional expression for if-else one-liner
        dataframe.at[index, "distance_from_last_coord"] = (
            euclidean_distance_between_coords if euclidean_distance_between_coords > epsilon else float("nan")
        )

    dataframe = dataframe.dropna()
    return dataframe


def get_output_file_path(device, date, location):
    # Get the current file location
    current_script_path = os.path.realpath(__file__)
    # Get the base directory
    base_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

    output_directory = os.path.join(base_directory, "output", f"{date}")

    output_filename = f"{device}_{date}_{location}_analysis.csv"

    os.makedirs(output_directory, exist_ok=True)
    output_file_path = os.path.join(output_directory, output_filename)

    return output_file_path

def main(date="22_04", systematic_error="0.137", epsilon="0.2", device="Xiaomi", location="Staadion"):
    raw_rover, processed_rover, ground_truth = read_data_files(date)

    converted_processed = replace_WGS84_with_LEST97(processed_rover)
    converted_raw = replace_WGS84_with_LEST97(raw_rover)
    converted_ground_truth = replace_WGS84_with_LEST97(ground_truth)

    ground_truth_with_euclidean = add_ground_truth_euclidean(converted_ground_truth, epsilon)

    processed_merged, raw_merged = merge_dataframes(converted_raw, converted_processed, ground_truth_with_euclidean)

    processed_without_systematic_error = remove_systematic_error_from_dataframe(processed_merged, systematic_error)
    raw_without_systematic_error = remove_systematic_error_from_dataframe(raw_merged, systematic_error)

    raw_distances = []
    processed_distances = []

    for index, row in processed_without_systematic_error.iterrows():
        # Drawing related operations
        # min_x, min_y = find_min_lest97_coordinates(processed_merged)
        # processed_deviation = draw_coordinates_and_their_connection(row, 'go-', 'bo', 'ro', 0, min_x, min_y)

        processed_deviation = calculate_deviation(0, row)
        processed_distances.append(processed_deviation)

    processed_without_systematic_error['deviation'] = processed_distances

    for index, row in raw_without_systematic_error.iterrows():
        # Drawing related operations
        # min_x, min_y = find_min_lest97_coordinates(raw_merged)
        # raw_deviation = draw_coordinates_and_their_connection(row, 'ro-', 'bo', 'go',0, min_x, min_y)

        raw_deviation = calculate_deviation(0, row)
        raw_distances.append(raw_deviation)

    raw_without_systematic_error['deviation'] = raw_distances

    processed_w_satellites = processed_without_systematic_error.merge(raw_without_systematic_error[['time', 'num_of_galileo_E1_freq_satellites',
                                                          'num_of_galileo_E5_freq_satellites',
                                                          'num_of_GPS_L1_freq_satellites',
                                                          'num_of_GPS_L5_freq_satellites',
                                                          'Cn0DbHz_epoch_average',
                                                          'pseudorange_rate_meters_per_second_epoch_average']], on='time',how='left')


    processed_w_satellites.to_csv(get_output_file_path(device, date, location))

    raw_mean_deviation = np.mean(raw_distances)
    processed_mean_deviation = np.mean(processed_distances)

    raw_standard_uncertainty = calculate_standard_deviation(raw_distances)
    processed_standard_uncertainty = calculate_standard_deviation(processed_distances)

    subtraction_of_raw_and_processed_mean_deviation = raw_mean_deviation - processed_mean_deviation
    subtraction_of_raw_and_processed_standard_uncertainty = raw_standard_uncertainty - processed_standard_uncertainty

    # Drawing
    # plt.figure(dpi=400)
    # plt.savefig('test_plot.svg', format='svg')
    # plt.xlim(0, 60)
    # plt.ylim(0, 60)
    # plt.show()

    return raw_mean_deviation, processed_mean_deviation, raw_standard_uncertainty, processed_standard_uncertainty, subtraction_of_raw_and_processed_mean_deviation, subtraction_of_raw_and_processed_standard_uncertainty

if __name__ == "__main__":
    main()
