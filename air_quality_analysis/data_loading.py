# loading the official uci air quality files
# the csv is european style: ';' between fields, ',' for decimals
# both file formats mark missing measurements with the code -200
# we turn that -200 into real nan values and build one timestamp column

import os

import numpy
import pandas

import air_quality_analysis.constants as constants


def _read_raw_frame(file_path):
    # just read the file, no cleaning yet
    # raises valueerror if it is not a csv or xlsx file
    file_path_text = str(file_path)
    extension = os.path.splitext(file_path_text)[1].lower()
    if extension == ".xlsx":
        return pandas.read_excel(file_path_text, sheet_name=constants.XLSX_SHEET_NAME)
    elif extension == ".csv":
        return pandas.read_csv(
            file_path_text,
            sep=constants.CSV_SEPARATOR,
            decimal=constants.CSV_DECIMAL_MARK,
        )
    else:
        raise ValueError("Unsupported file extension: {}".format(extension))


def _check_required_columns(data_frame):
    # Date + Time are needed for the timestamp, nothing works without them
    missing_columns = []
    for column_name in ["Date", "Time"]:
        if column_name not in data_frame.columns:
            missing_columns.append(column_name)
    if missing_columns:
        raise ValueError("Missing required columns: {}".format(missing_columns))


def _build_timestamp_series(data_frame):
    # glue Date and Time together into one timestamp column
    # csv dates are text like 10/03/2004 -> need dayfirst=True there
    # xlsx dates are already datetime objects -> no dayfirst needed
    # times look like 18.00.00 so swap the dots for colons first
    date_column = data_frame["Date"]
    if pandas.api.types.is_datetime64_any_dtype(date_column):
        date_text = date_column.dt.strftime("%Y-%m-%d")
        day_first = False
    else:
        date_text = date_column.astype(str)
        day_first = True
    time_text = data_frame["Time"].astype(str)
    time_text = time_text.str.replace(".", ":", regex=False)
    timestamp_series = pandas.to_datetime(
        date_text + " " + time_text,
        dayfirst=day_first,
        errors="raise",
    )
    return timestamp_series


def _convert_measurement_columns(data_frame):
    # everything except Date/Time/timestamp is a measurement
    # make it numeric, then swap the -200 missing code for nan
    measurement_columns = []
    for column_name in data_frame.columns:
        if column_name != "Date" and column_name != "Time" and column_name != "timestamp":
            measurement_columns.append(column_name)
    for column_name in measurement_columns:
        numeric_series = pandas.to_numeric(data_frame[column_name], errors="coerce")
        data_frame[column_name] = numeric_series.replace(
            constants.MISSING_VALUE_CODE, numpy.nan
        )
    return data_frame


def load_air_quality(file_path):
    # load one official file and return it cleaned up:
    #   - timestamp column added
    #   - -200 gone (becomes nan)
    #   - rows sorted by time, fresh row index
    #   - duplicate timestamps are rejected
    # trailing blank rows / columns in the official files get dropped too
    data_frame = _read_raw_frame(file_path)
    data_frame = data_frame.dropna(axis=0, how="all")
    data_frame = data_frame.dropna(axis=1, how="all")
    data_frame = data_frame.copy()
    _check_required_columns(data_frame)
    data_frame["timestamp"] = _build_timestamp_series(data_frame)
    data_frame = _convert_measurement_columns(data_frame)
    data_frame = data_frame.sort_values("timestamp")
    data_frame = data_frame.reset_index(drop=True)
    if data_frame["timestamp"].duplicated().any():
        raise ValueError("Duplicate timestamps found in the input data")
    return data_frame
