import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas import read_csv
from coordinates.converter import CoordinateConverter, WGS84, L_Est97

converter = CoordinateConverter()

# Read the files in (needs to be changed according to file)
# If sth is broken then the delimiter is the most likely answer (save .csv file in Excel and then it works)
def read_data_files():
    raw_rover = read_csv("input/Standardhälve arvutamine - [Staadion] Toorandmed.csv", delimiter=";")
    processed_rover = read_csv("input/Standardhälve arvutamine - [Staadion] Järeltööötlus.csv", delimiter=";")
    ground_truth = read_csv("input/Standardhälve arvutamine - [Staadion] Tõeandmed.csv", delimiter=";")
    return raw_rover, processed_rover, ground_truth

# Merging dataframes
def merge_dataframes(raw_rover, processed_rover, ground_truth):
    processed_merged = pd.merge(processed_rover, ground_truth, on="time")
    raw_merged = pd.merge(raw_rover, ground_truth, on="time")
    return processed_merged, raw_merged

def calculate_euclidean_distance(coord1: L_Est97, coord2: L_Est97):
    return math.sqrt((coord1.x - coord2.x) ** 2 + (coord1.y - coord2.y) ** 2)

def wgs84_to_lest97_coordinates(latitudes, longitudes):
    coordinates_wgs84 = np.column_stack((latitudes, longitudes))
    return [converter.wgs84_to_l_est97(WGS84(lat=lat, long=long)) for lat, long in coordinates_wgs84]

def find_min_lest97_coordinates(dataframe):
    latitudes = dataframe['latitude_x'].to_numpy()
    longitudes = dataframe['longitude_x'].to_numpy()
    coordinates_lest97 = wgs84_to_lest97_coordinates(latitudes, longitudes)
    return min(coord.x for coord in coordinates_lest97) - 10, min(coord.y for coord in coordinates_lest97) - 10

def draw_coordinates_and_their_connection(row, line_color, truth_color, rover_color, deviation, min_x, min_y):
    # Converting rover coordinates to LEST97
    rover_coord_wgs84 = WGS84(lat=row['latitude_x'], long=row['longitude_x'])
    rover_coord_lest97 = converter.wgs84_to_l_est97(rover_coord_wgs84)

    # Converting ground truth coordinates to LEST97
    ground_truth_coord_wgs84 = WGS84(lat=row['latitude_y'], long=row['longitude_y'])
    ground_truth_coord_lest97 = converter.wgs84_to_l_est97(ground_truth_coord_wgs84)

    # Incrementing deviation
    deviation += calculate_euclidean_distance(rover_coord_lest97, ground_truth_coord_lest97)

    # Plotting
    plt.plot([rover_coord_lest97.x - min_x, ground_truth_coord_lest97.x - min_x],
             [rover_coord_lest97.y - min_y, ground_truth_coord_lest97.y - min_y], line_color, markersize=1)
    plt.plot([ground_truth_coord_lest97.x - min_x], [ground_truth_coord_lest97.y - min_y], truth_color, markersize=1.2)
    plt.plot([rover_coord_lest97.x - min_x], [rover_coord_lest97.y - min_y], rover_color, markersize=1.2)

    return deviation

def calculate_standard_deviation(distances):
    mean_distance = np.mean(distances)
    squared_diff = [(d - mean_distance) ** 2 for d in distances]
    variance = np.mean(squared_diff)
    standard_deviation = np.sqrt(variance)
    return standard_deviation

def main():
    raw_rover, processed_rover, ground_truth = read_data_files()
    processed_merged, raw_merged = merge_dataframes(raw_rover, processed_rover, ground_truth)

    plt.figure(dpi=600)

    min_x, min_y = find_min_lest97_coordinates(raw_merged)

    raw_distances = []
    processed_distances = []

    for index, row in processed_merged.iterrows():
        processed_deviation = draw_coordinates_and_their_connection(row, 'go-', 'bo', 'ro',
                                                                     0, min_x, min_y)
        processed_distances.append(processed_deviation)

    for index, row in raw_merged.iterrows():
        raw_deviation = draw_coordinates_and_their_connection(row, 'ro-', 'bo', 'go',
                                                               0, min_x, min_y)
        raw_distances.append(raw_deviation)

    raw_mean_deviation = np.mean(raw_distances)
    processed_mean_deviation = np.mean(processed_distances)

    print(raw_mean_deviation, " Toorandmete ja tõeandmete keskmine viga")
    print(processed_mean_deviation, " Järeltöötlus andmete ja tõeandmete keskmine viga")

    raw_standard_deviation = calculate_standard_deviation(raw_distances)
    processed_standard_deviation = calculate_standard_deviation(processed_distances)

    print(raw_standard_deviation, " Toorandmete ja tõeandmete standardhälve")
    print(processed_standard_deviation, " Järeltöötlus andmete ja tõeandmete standardhälve")

    plt.savefig('test_plot.svg', format='svg')
    plt.xlim(0, 60)
    plt.ylim(0, 60)
    plt.show()

if __name__ == "__main__":
    main()


# ToDod
# Toorandmete rea lisamine [DONE]
# Saa väiksemaks see tradi roheline joon
# Arvutaks toorandmete/järeltöötlusandmete ja tõeandmete vahelise standardhälve
#
# Lahutada kõikidest koordinaatidest maha esimene (või kõige väiksem) koordinaat [DONE]
# Miinimum, maksimum väärtus [DONE]
# Esimesed 15 minutit viska minema [DONE]
# Teha vektor failiks [DONE]
