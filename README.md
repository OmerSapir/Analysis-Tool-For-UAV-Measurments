# Vertical Profile Analysis Tool For Atmospheric Properties Measured By UAV “Stairs” Method

## Background
Our laboratory researches the chemical and physical properties of various aerosols and their impact on atmospheric processes, climate, and human health. We use advanced techniques to monitor aerosols in the atmosphere, including an emerging in-situ aerosol detection method using UAVs (Unmanned Aerial Vehicles) equipped with sensitive sensors to detect vertical profiles. The monitoring process involves a "stairs" protocol where the UAV ascends to a specific height, hovers for a few seconds, then ascends to the next height, repeating the process. During this time, atmospheric properties are continuously measured by the sensors with a focus on the mean hovering periods data (steps) rather than the ascent periods data.

## Project Goal
The goal of this project is to develop a semi-automated system to extract and analyze the relevant measured data. Due to the inaccuracy of existing altimeters, the pressure variable is used as an altitude indicator. The system will process the measurement results in the CSV files, construct a pressure profile graph, and identify the straight portions representing the hovering "steps". The system will provide timestamp recommendations for the start and end of each step. Users will be able to select relevant steps, remove unwanted portions from the data, and create a clean correlation graph between pressure and chosen measured variables.


## User Instructions
1. **Browse and Select CSV File:** Use the GUI to browse and select the CSV file.
2. **Specify Parameters:** Input the index column, analysis (pressure) column, statistics (measurement) column, steps size, and variance threshold.
3. **Plot and Select Intervals:** The program will plot the pressure data with suggested intervals. You can select and subtract unwanted intervals.
4. **Plot Statistics:** After exiting the pressure plot, confirm if you want to plot the statistics for the selected intervals.
5. **Save Intervals:** After exiting the statistics plot, you can choose to save the selected intervals as a JSON file.

![Download Video Demo](https://github.com/OmerSapir/Analysis-Tool-For-UAV-Measurments/blob/main/Example.mp4)

## Input
CSV file containing the following columns:
- Timestamp
- Pressure
- Measurable atmospheric composition parameters


### Installing the dependencies:
To install the required packages listed in requirements.txt, run the following command:
```
pip install -r requirements.txt
```

### Testing the program:
To test the program, run:
```
pytest
```

### Running the program:
To run the program, execute:
```
python UAV_steps_analysis.py
```

This project was originally implemented as part of the [Python programming course](https://github.com/szabgab/wis-python-course-2024-04) at the [Weizmann Institute of Science](https://www.weizmann.ac.il/) taught by [Gabor Szabo](https://szabgab.com/).


