# test 01 - a first look at the raw air quality dataset
# run it with:  python test_01_explore_dataset.py
# it just reads the csv and prints the basic facts, no project code involved yet

import os

import pandas

# find the csv next to this script so the demo works from any folder
base_directory = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_directory, "data", "AirQualityUCI.csv")

# the file is european style: ';' between fields, ',' for decimals
data_frame = pandas.read_csv(csv_path, sep=";", decimal=",")

# the file ends with a bunch of empty rows and one empty column, drop them
data_frame = data_frame.dropna(axis=0, how="all")
data_frame = data_frame.dropna(axis=1, how="all")

print("=== raw uci air quality dataset ===")
print("rows x columns:", data_frame.shape[0], "x", data_frame.shape[1])
print("first record:", data_frame["Date"].iloc[0], data_frame["Time"].iloc[0])
print("last record:", data_frame["Date"].iloc[-1], data_frame["Time"].iloc[-1])

print()
print("column names:")
for column_name in data_frame.columns:
    print("   ", column_name)

# -200 is the official code for "sensor had no data", count how often it shows up
print()
print("how often the missing code -200 appears:")
for column_name in data_frame.columns:
    if column_name == "Date" or column_name == "Time":
        continue
    missing_count = int((data_frame[column_name] == -200).sum())
    print("   ", column_name, "->", missing_count)

# a tiny sample so you can see what the rows look like
print()
print("first 3 rows of a few columns:")
print(data_frame[["Date", "Time", "CO(GT)", "PT08.S1(CO)", "T", "RH"]].head(3))
