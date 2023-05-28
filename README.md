# GNSS data processing scripts

GNSS data processing scripts are a collection of Python scripts for analyzing Android GNSS data.

## Requirements

To use the program, you must have at least Python 3.9, installed coordinates.converter, and numpy.

## Configuration

Change values in configuration.yaml file to match your needs. main.py uses those values.

## Input folder
Make an input folder and nest a date folder (matching the one in configuration.yaml), that includes Android GNSS raw data log (.txt), post-processed Android GNSS data from RTKPOST (.pos), and reference data from u-blox (.ubx) by date (dd_mm).

```bash
gnss_data_processing_scripts
|--automated_calculation
    |--input
        |--dd_mm
           |--raw_data_001.txt
           |--processed_data_001.ubx
           |--reference_data_001.pos
        |--dd_mm
           |--raw_data_002.txt
           |--processed_data_002.ubx
           |--reference_data_002.pos
```
NB! If you don't provide all 3 files then script won't calculate results. It will still convert all of the provided files into csv.  format.

## Output files

Ground_truth_{date}_{location}.csv
File contains 
- rover latitude/longitude WGS84 coordinates
- datetime stamps (secong accuracy)

{device}_Fix_{provider}_{date}_{location}.csv
File contains 
- rover Fix latitude/longitude WGS84 coordinates
- datetime stamps (secong accuracy)
- number of satellites seen using Galileo E1 frequency in current epoch
- number of satellites seen using Galileo E5 frequency in current epoch
- number of satellites seen using GPS L1 frequency in current epoch
- number of satellites seen using GPS L5 frequency in current epoch
- Average of Cn0DbHz in current epoch
- Pseudorange rate meters per secong average in current epoch

{device}_pos_{provider}_{date}_{location}.csv
File contains
- rover latitude/longitude WGS84 coordinates
- datetime stamps (secong accuracy)

{device}_{date}_{location}_analysis.csv
This file is a combination of processed android GNSS data and ground truth information. Coordinates or provided in L_Est97 format.

Results_{constellations}_{device}_{date}_{location}.csv
In this file you can see the calculation results (standard deviation and mean error between rover and ground truth)

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.
