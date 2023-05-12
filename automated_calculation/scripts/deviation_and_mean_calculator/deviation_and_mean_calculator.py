import math
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from pandas import read_csv
from coordinates.converter import CoordinateConverter, WGS84, L_Est97

EPSILON = 0.2
# ToDo should probably placed elsewhere
DISTANCE_ERROR = 0.26

converter = CoordinateConverter()


# Read the files in (needs to be changed according to file)
def read_data_files(date, input_folder=None):
    if input_folder is None:
        # Get the current file location
        current_script_path = os.path.realpath(__file__)

        # Get the base directory
        base_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

        # Set the default input folder
        input_folder = os.path.join(base_directory, "output", date)

    input_path = Path(input_folder)

    file_names = [file.name for file in input_path.iterdir() if file.is_file() and file.suffix == ".csv"]

    raw_rover_data_file = [file_name for file_name in file_names if "Fix" in file_name][0]
    processed_rover_data_file = [file_name for file_name in file_names if "pos" in file_name][0]
    ground_truth_data_file = [file_name for file_name in file_names if "Referentsandmed" in file_name][0]

    raw_rover_file = input_path / raw_rover_data_file
    processed_rover_file = input_path / processed_rover_data_file
    ground_truth_file = input_path / ground_truth_data_file

    # Change delimiter if necessary (Excel and Google sheets have different values ; and , accordingly)
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


# ToDo Rename function more properly
def remove_systematic_error_from_dataframe(merged_dataframe):
    result_dataframe = merged_dataframe.copy()
    for index, row in result_dataframe.iterrows():
        if index == 0:
            continue

        # ToDo look over if they should be x or y
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
                                                              DISTANCE_ERROR)

        result_dataframe.at[index, "rover_latitude"] = new_rover_coordinate.x
        result_dataframe.at[index, "rover_longitude"] = new_rover_coordinate.y

    return result_dataframe

def calculate_direction_vector(current_coord, previous_coord):
    return L_Est97(current_coord.x - previous_coord.x, current_coord.y - previous_coord.y)


# ToDo Division my have to be overlooked
def normalize_direction_vector(direction_vector, direction_length_vector):
    return L_Est97(direction_vector.x / direction_length_vector, direction_vector.y / direction_length_vector)


# def calculate_new_rover_coordinate(normalised_direction_vector, current_rover_coordinate, distance_error):
#     return L_Est97(distance_error * normalised_direction_vector.x + current_rover_coordinate.x,
#                    distance_error * normalised_direction_vector.y + current_rover_coordinate.y)

def calculate_new_rover_coordinate(normalised_direction_vector, current_rover_coordinate, distance_error):
    return L_Est97(current_rover_coordinate.x - distance_error * normalised_direction_vector.x,
                    current_rover_coordinate.y - distance_error * normalised_direction_vector.y)


def calculate_deviation(deviation, row):
    # Incrementing deviation
    rover_coord_lest97 = L_Est97(row["rover_latitude"], row["rover_latitude"])
    ground_truth_coord_lest97 = L_Est97(row["ground_truth_latitude"], row["ground_truth_latitude"])
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


# ToDo Add constant for the -10 (ask Juhan for reference)
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


def add_ground_truth_euclidean(dataframe):
    for index, row in dataframe.iterrows():
        if index == 0:
            continue

        previous_row = dataframe.iloc[index - 1]

        current_coord = L_Est97(row["latitude"], row["longitude"])
        previous_coord = L_Est97(previous_row["latitude"], previous_row["longitude"])

        euclidean_distance_between_coords = calculate_euclidean_distance(current_coord, previous_coord)

        # Ternary conditional expression for if-else one-liner
        dataframe.at[index, "distance_from_last_coord"] = (
            euclidean_distance_between_coords if euclidean_distance_between_coords > EPSILON else float("nan")
        )

    dataframe = dataframe.dropna()
    return dataframe


# This function removes first 15 min of data from all files (since it is gathered for initial positioning)
# Unnecessary function
def filter_time_range(dataframe):
    start_time = dataframe['time'].min() + pd.Timedelta(minutes=15)
    end_time = dataframe['time'].max() - pd.Timedelta(seconds=15)
    return dataframe[(dataframe['time'] >= start_time) & (dataframe['time'] <= end_time)]


# Needs redoing
def main(date="21_04"):
    # draft main
    # 1. read data
    # 2. replace WGS84 w LEST97
    # 3. add euclidean distances (and remove NaN values)
    # 4. Merge dataframes
    # 5. Math() will replace current rover coordinates with fixed ones

    raw_rover, processed_rover, ground_truth = read_data_files(date)

    # print(processed_rover, " processed_rover")
    print(raw_rover, " raw_rover")

    # This removes first 15 min. If use smaller circles then comment out
    # raw_rover = filter_time_range(raw_rover)
    # processed_rover = filter_time_range(processed_rover)
    # ground_truth = filter_time_range(ground_truth)

    converted_processed = replace_WGS84_with_LEST97(processed_rover)
    converted_raw = replace_WGS84_with_LEST97(raw_rover)
    converted_ground_truth = replace_WGS84_with_LEST97(ground_truth)

    ground_truth_with_euclidean = add_ground_truth_euclidean(converted_ground_truth)

    # print(ground_truth_with_euclidean)

    processed_merged, raw_merged = merge_dataframes(converted_raw, converted_processed, ground_truth_with_euclidean)

    aftermath_processed = remove_systematic_error_from_dataframe(processed_merged)
    aftermath_raw = remove_systematic_error_from_dataframe(raw_merged)

    raw_distances = []
    processed_distances = []

    for index, row in aftermath_processed.iterrows():
        # Drawing related operations
        # min_x, min_y = find_min_lest97_coordinates(processed_merged)
        # processed_deviation = draw_coordinates_and_their_connection(row, 'go-', 'bo', 'ro', 0, min_x, min_y)

        processed_deviation = calculate_deviation(0, row)
        processed_distances.append(processed_deviation)

    aftermath_processed['deviation'] = processed_distances

    for index, row in aftermath_raw.iterrows():
        # Drawing related operations
        # min_x, min_y = find_min_lest97_coordinates(raw_merged)
        # raw_deviation = draw_coordinates_and_their_connection(row, 'ro-', 'bo', 'go',0, min_x, min_y)

        raw_deviation = calculate_deviation(0, row)
        raw_distances.append(raw_deviation)

    aftermath_raw['deviation'] = raw_distances


    aftermath_raw.to_csv("raw_aftermath.csv")
    aftermath_processed.to_csv("proc_aftermath.csv")

    # ToDo should be implemented in better manner
    testing_df = aftermath_processed.merge(aftermath_raw[['time', 'num_of_galileo_E1_freq_satellites',
                                                          'num_of_galileo_E5_freq_satellites',
                                                          'num_of_GPS_L1_freq_satellites',
                                                          'num_of_GPS_L5_freq_satellites']], on='time',how='left')
    testing_df.to_csv("testing_aftermath.csv")


    raw_mean_deviation = np.mean(raw_distances)
    processed_mean_deviation = np.mean(processed_distances)


    # print(processed_merged, " processed calculated")
    # print(converted_processed, " processed converted")
    # print(raw_merged, " raw calculated")
    # print(converted_raw, " raw converted")

    print(raw_mean_deviation, " Toorandmete ja referentsandmete keskmine viga")
    print(processed_mean_deviation, " Järeltöötlus andmete ja referentsandmete keskmine viga")

    raw_standard_deviation = calculate_standard_deviation(raw_distances)
    processed_standard_deviation = calculate_standard_deviation(processed_distances)

    print(raw_standard_deviation, " Toorandmete ja referentsandmete standardhälve")
    print(processed_standard_deviation, " Järeltöötlus andmete ja referentsandmete standardhälve")

    subtraction_of_raw_and_processed_mean_deviation = raw_mean_deviation - processed_mean_deviation
    subtraction_of_raw_and_processed_standard_deviation = raw_standard_deviation - processed_standard_deviation

    # Drawing
    # plt.figure(dpi=400)
    # plt.savefig('test_plot.svg', format='svg')
    # plt.xlim(0, 60)
    # plt.ylim(0, 60)
    # plt.show()

    return raw_mean_deviation, processed_mean_deviation, raw_standard_deviation, processed_standard_deviation, subtraction_of_raw_and_processed_mean_deviation, subtraction_of_raw_and_processed_standard_deviation


if __name__ == "__main__":
    main()
