# shared constants, nothing fancy

MISSING_VALUE_CODE = -200  # this is what the official files use for "no data"
XLSX_SHEET_NAME = "AirQualityUCI"
CSV_SEPARATOR = ";"        # the csv is european style
CSV_DECIMAL_MARK = ","     # ...so decimals use a comma

# the three sensor / reference pairs we care about
# (PT08 sensor response column, matching reference analyzer column)
SENSOR_REFERENCE_PAIRS = [
    ("PT08.S1(CO)", "CO(GT)"),
    ("PT08.S3(NOx)", "NOx(GT)"),
    ("PT08.S4(NO2)", "NO2(GT)"),
]
