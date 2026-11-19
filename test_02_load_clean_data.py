# test 02 - load the raw files through our cleaning module
# run it with:  python test_02_load_clean_data.py
# shows the before / after of the cleaning: -200 becomes nan, timestamps appear

import os
import sys

# make sure python can find the air_quality_analysis package
base_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_directory)

from air_quality_analysis.data_loading import load_air_quality

csv_path = os.path.join(base_directory, "data", "AirQualityUCI.csv")
xlsx_path = os.path.join(base_directory, "data", "AirQualityUCI.xlsx")

# load the csv first and look at what changed
data_frame = load_air_quality(csv_path)

print("=== cleaned csv ===")
print("rows x columns:", data_frame.shape[0], "x", data_frame.shape[1])
print("time range:", data_frame["timestamp"].iloc[0], "->", data_frame["timestamp"].iloc[-1])
print("duplicate timestamps:", int(data_frame["timestamp"].duplicated().sum()))
print()
print("missing values per column (the -200 codes are gone):")
for column_name in data_frame.columns:
    if column_name == "Date" or column_name == "Time" or column_name == "timestamp":
        continue
    missing_count = int(data_frame[column_name].isna().sum())
    print("   ", column_name, "->", missing_count)

# now the xlsx version, should give the same shape
xlsx_frame = load_air_quality(xlsx_path)
print()
print("=== cleaned xlsx ===")
print("rows x columns:", xlsx_frame.shape[0], "x", xlsx_frame.shape[1])
print("time range:", xlsx_frame["timestamp"].iloc[0], "->", xlsx_frame["timestamp"].iloc[-1])

# a little sanity check: both files should agree on the first CO(GT) value
print()
print("first CO(GT) from csv:", data_frame["CO(GT)"].iloc[0])
print("first CO(GT) from xlsx:", xlsx_frame["CO(GT)"].iloc[0])
