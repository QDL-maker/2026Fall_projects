# tests for the data loading module
# tiny fake csv files are written to a temp folder, no real data needed

import os
import sys
import tempfile
import unittest

import pandas

REPOSITORY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPOSITORY_ROOT)

from air_quality_analysis.data_loading import load_air_quality


class DataLoadingTests(unittest.TestCase):

    def _write_text_file(self, directory_path, file_name, text):
        # helper: drop some text into a temp file and hand back the path
        file_path = os.path.join(directory_path, file_name)
        output_file = open(file_path, "w", encoding="utf-8")
        try:
            output_file.write(text)
        finally:
            output_file.close()
        return file_path

    def test_csv_file_loads_with_semicolon_and_comma_decimals(self):
        # the european csv format: semicolons between fields, comma decimals
        text = (
            "Date;Time;CO(GT);T;RH\n"
            "10/03/2004;18.00.00;2,6;13,6;48,9\n"
        )
        with tempfile.TemporaryDirectory() as directory_path:
            file_path = self._write_text_file(directory_path, "AirQualityUCI.csv", text)
            result = load_air_quality(file_path)
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result.loc[0, "timestamp"], pandas.Timestamp("2004-03-10 18:00:00")
        )
        self.assertAlmostEqual(result.loc[0, "CO(GT)"], 2.6)
        self.assertAlmostEqual(result.loc[0, "T"], 13.6)
        self.assertAlmostEqual(result.loc[0, "RH"], 48.9)

    def test_missing_value_code_becomes_not_a_number(self):
        # -200 must come out as nan, never as the number -200
        text = (
            "Date;Time;CO(GT);T;RH\n"
            "10/03/2004;18.00.00;-200;13,6;48,9\n"
            "10/03/2004;19.00.00;2,0;-200;47,7\n"
        )
        with tempfile.TemporaryDirectory() as directory_path:
            file_path = self._write_text_file(directory_path, "AirQualityUCI.csv", text)
            result = load_air_quality(file_path)
        self.assertTrue(pandas.isna(result.loc[0, "CO(GT)"]))
        self.assertTrue(pandas.isna(result.loc[1, "T"]))
        self.assertAlmostEqual(result.loc[0, "T"], 13.6)
        self.assertAlmostEqual(result.loc[1, "CO(GT)"], 2.0)

    def test_rows_are_sorted_by_timestamp(self):
        # rows given out of order should come back sorted by time
        text = (
            "Date;Time;CO(GT)\n"
            "11/03/2004;10.00.00;1,5\n"
            "10/03/2004;18.00.00;2,6\n"
        )
        with tempfile.TemporaryDirectory() as directory_path:
            file_path = self._write_text_file(directory_path, "AirQualityUCI.csv", text)
            result = load_air_quality(file_path)
        self.assertEqual(
            result.loc[0, "timestamp"], pandas.Timestamp("2004-03-10 18:00:00")
        )
        self.assertEqual(
            result.loc[1, "timestamp"], pandas.Timestamp("2004-03-11 10:00:00")
        )

    def test_duplicate_timestamps_raise_error(self):
        # same timestamp twice -> something is wrong with the file
        text = (
            "Date;Time;CO(GT)\n"
            "10/03/2004;18.00.00;2,6\n"
            "10/03/2004;18.00.00;2,7\n"
        )
        with tempfile.TemporaryDirectory() as directory_path:
            file_path = self._write_text_file(directory_path, "AirQualityUCI.csv", text)
            with self.assertRaises(ValueError):
                load_air_quality(file_path)

    def test_unsupported_file_extension_raises_error(self):
        # we only speak csv and xlsx
        with tempfile.TemporaryDirectory() as directory_path:
            file_path = self._write_text_file(directory_path, "AirQualityUCI.txt", "x")
            with self.assertRaises(ValueError):
                load_air_quality(file_path)

    def test_missing_date_column_raises_error(self):
        # no Date column means no timestamps, so refuse to load
        text = (
            "Time;CO(GT)\n"
            "18.00.00;2,6\n"
        )
        with tempfile.TemporaryDirectory() as directory_path:
            file_path = self._write_text_file(directory_path, "AirQualityUCI.csv", text)
            with self.assertRaises(ValueError):
                load_air_quality(file_path)

    def test_all_empty_rows_are_dropped(self):
        # the real files have blank rows at the end, they should vanish
        text = (
            "Date;Time;CO(GT)\n"
            "10/03/2004;18.00.00;2,6\n"
            ";;\n"
            "11/03/2004;10.00.00;1,5\n"
        )
        with tempfile.TemporaryDirectory() as directory_path:
            file_path = self._write_text_file(directory_path, "AirQualityUCI.csv", text)
            result = load_air_quality(file_path)
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
