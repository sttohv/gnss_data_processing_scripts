# How to use application

## Input files
- Android gnss data (.txt)
- u-blox receiver data (.ubx)
- post processed Android gnss data from RTKPOST (.pos)

## Output files

The file conversions from native format to csv are needed in order to calculate results

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

NB! If you don't provide all 3 files then script won't calculate results. It will still convert all of the provided files into csv. 

format.
