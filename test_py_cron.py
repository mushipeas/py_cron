import datetime
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from py_cron import import_pctab, parse_pctab, time_left, run_task


class Test_import_pctab(unittest.TestCase):
    def test_Pathlike_object(self):
        res = import_pctab(["."])
        self.assertIsInstance(res, Path)

    def test_output(self):
        testfile = "testfile.txt"
        res = import_pctab([testfile])
        self.assertEqual(res, Path(testfile))


class Test_parse_pctab(unittest.TestCase):
    def test_output(self):
        input_text = ["0 1 2 3 4 Task1\n", "5 6 7 8 9 Task2 -a -b -c\n"]
        testfile = Path("testfile.txt")
        with testfile.open("w") as fp:
            fp.writelines(input_text)

        res = parse_pctab(testfile)
        self.assertEqual(res[0], ["0 1 2 3 4", ["Task1"]])
        self.assertEqual(res[1], ["5 6 7 8 9", ["Task2", "-a", "-b", "-c"]])


class Test_time_left(unittest.TestCase):
    def test_timedelta(self):
        datetime_mock = Mock(wraps=datetime.datetime)
        datetime_mock.now.return_value = datetime.datetime(2020, 1, 1)

        with patch("datetime.datetime", new=datetime_mock):
            res = time_left(datetime.datetime(2020, 1, 2))
            self.assertEqual(res, 86400)  # 1 day apart


if __name__ == "__main__":
    unittest.main()
