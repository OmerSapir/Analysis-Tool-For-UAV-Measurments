# Vertical Profile Analysis Tool For Atmospheric Properties Measured By UAV “Stairs” Method

## Background
Our laboratory researches the chemical and physical properties of various aerosols and their impact on atmospheric processes, climate, and human health. We use advanced techniques to monitor aerosols in the atmosphere, including an emerging in-situ aerosol detection method using UAVs (Unmanned Aerial Vehicles) equipped with sensitive sensors to detect vertical profiles. The monitoring process involves a "stairs" protocol where the UAV ascends to a specific height, hovers for a few seconds, then ascends to the next height, repeating the process. During this time, atmospheric properties are continuously measured by the sensors with a focus on the mean hovering periods data rather than the ascent periods data.
<p align="center">
<img src="matrice600.jpg" width="250" height="300">

## Project Goal
My goal is to develop a semi-automated system to extract and analyze the relevant measured data. Due to the inaccuracy of the existing altimeters, we use the pressure variable as an altitude indicator. The system will process the measurement results in the CSV files, construct a pressure profile graph, and identify the straight portions representing the hovering "stairs". The system will provide timestamp recommendations for the start and end of each step, flagging any potentially erroneous data points. Users will be able to select relevant steps, remove unwanted portions from the data, and create a clean correlation graph between pressure and chosen measured variables.

## Technical Logic
1. Receiving the CSV file, sliding window size, variance threshold, and error point threshold from the user.
2. Converting the CSV file into a DataFrame using timestamps as the index column.
3. Defining a function to locate low-variance windows based on start and end timestamps.
4. Defining a function to detect error points using timestamps.
5. Applying both variance and error detection functions to the pressure column using a sliding window iteration.
6. Returning timestamp period suggestions for the relevant filtered measurements and plotting a graph of the pressure data with the suggested periods marked.
7. Allowing the user to extract and exclude unwanted suggested periods.
8. Applying a function to calculate the mean and standard deviation for the chosen measurement column.
9. Plotting a vertical profile graph showing the change of the selected variable over time.

## Input
CSV file containing the following columns:
- Timestamp
- Pressure
- Measurable atmospheric composition parameters

### Variables
- `filename`: name of the CSV file
- `window_size`: length of the average hovering time in seconds
- `var_ths`: variance threshold
- `err_ths`: error point threshold

### Installing the dependencies:
The required packeges are in `requirements.txt`
```
pip install -r requirements.txt
```

### Testing the program:
To test the program:
```
pytest
```

### Running the program:
To run the program, provide the CSV file name, window length, variance threshold and error point threshold:
```
python stairs_analysis.py filename window_size var_ths err_ths
```

This project was originally implemented as part of the [Python programming course](https://github.com/szabgab/wis-python-course-2024-04) at the [Weizmann Institute of Science](https://www.weizmann.ac.il/) taught by [Gabor Szabo](https://szabgab.com/).
