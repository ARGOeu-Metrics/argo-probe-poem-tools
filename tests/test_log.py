import datetime
import os
import unittest
from unittest.mock import patch

from argo_probe_argo_tools.log import Log, _compare_datetimes, \
    CriticalException, WarnException

mock_ok_log = """
2022-08-01 04:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 04:00:05 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 04:00:05 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 04:00:43 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 06:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 06:00:04 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 06:00:04 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 06:00:44 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 08:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 08:00:04 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 08:00:04 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 08:00:42 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 10:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 10:00:05 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 10:00:05 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 10:00:44 - argo-poem-packages - INFO - The run finished successfully.
"""

mock_wrong_format1 = """
2022-08-01 04:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 04:00:05 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 04:00:05 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 04:00:43 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 06:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 06:00:04 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 06:00:04 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 06:00:44 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 08:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 08:00:04 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 08:00:04 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 08:00:42 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 10:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 10:00:05 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 10:00:44 - argo-poem-packages - INFO - The run finished successfully.
"""

mock_wrong_format2 = """
2022-08-01 04:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 04:00:05 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 04:00:05 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 04:00:43 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 06:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 06:00:04 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 06:00:04 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 06:00:44 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 08:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 08:00:04 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 08:00:04 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 08:00:42 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 10:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 10:00:05 - INFO - Creating YUM repo files...
2022-08-01 10:00:05 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 10:00:44 - argo-poem-packages - INFO - The run finished successfully.
"""

mock_wrong_format3 = """
2022-08-01 04:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 04:00:05 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 04:00:05 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 04:00:43 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 06:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 06:00:04 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 06:00:04 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 06:00:44 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 08:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 08:00:04 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 08:00:04 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 08:00:42 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 10:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 10:00:05 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 10:00:05 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 10:00:44 - argo-poem-packages - The run finished successfully.
"""

mock_ok_log_with_dash_in_msg = """
2022-08-01 04:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 04:00:05 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 04:00:05 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 04:00:43 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 06:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 06:00:04 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 06:00:04 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 06:00:44 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 08:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 08:00:04 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 08:00:04 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 08:00:42 - argo-poem-packages - INFO - The run finished successfully.
2022-08-01 10:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-08-01 10:00:05 - argo-poem-packages - INFO - Creating YUM repo files...
2022-08-01 10:00:05 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-08-01 10:00:44 - argo-poem-packages - INFO - The run finished - successfully.
"""

mock_log_with_warn = """
2022-07-19 10:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-07-19 10:00:06 - argo-poem-packages - INFO - Creating YUM repo files...
2022-07-19 10:00:06 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4-untested.repo; /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-07-19 10:00:48 - argo-poem-packages - WARNING - Packages not found with requested version: nagios-plugins-grycap-im-0.1.3
"""

mock_log_with_error = """
2022-07-11 12:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-07-11 12:00:04 - argo-poem-packages - INFO - Creating YUM repo files...
2022-07-11 12:00:04 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4-untested.repo; /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-07-11 12:00:25 - argo-poem-packages - ERROR - Error installing packages: Command '['yum', 'list', 'available', '--showduplicates']' returned non-zero exit status 1.
"""

mock_log_recovered = """
2022-07-11 12:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-07-11 12:00:04 - argo-poem-packages - INFO - Creating YUM repo files...
2022-07-11 12:00:04 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4-untested.repo; /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-07-11 12:00:25 - argo-poem-packages - ERROR - Error installing packages: Command '['yum', 'list', 'available', '--showduplicates']' returned non-zero exit status 1.
2022-07-11 13:00:02 - argo-poem-packages - INFO - Sending request for profile(s): ARGO_MON
2022-07-11 13:00:05 - argo-poem-packages - INFO - Creating YUM repo files...
2022-07-11 13:00:05 - argo-poem-packages - INFO - Created files: /etc/yum.repos.d/UMD-4.repo; /etc/yum.repos.d/argo.repo; /etc/yum.repos.d/epel.repo; /etc/yum.repos.d/etf.repo
2022-07-11 13:00:44 - argo-poem-packages - INFO - The run finished successfully.
"""


class CheckLogTests(unittest.TestCase):
    def setUp(self):
        self.logfile = "mock_file.log"
        self.logfile_wrong_format1 = "mock_file_wrong1.log"
        self.logfile_wrong_format2 = "mock_file_wrong2.log"
        self.logfile_wrong_format3 = "mock_file_wrong3.log"
        self.logfile_with_warn = "mock_file_warn.log"
        self.logfile_with_error = "mock_file_error.log"
        self.logfile_with_recovery = "mock_file_recovery.log"
        with open(self.logfile, "w") as f:
            f.write(mock_ok_log)
        self.log = Log(
            app="argo-poem-packages", logfile=self.logfile, age=2, timeout=10
        )
        self.log_missing_file = Log(
            app="argo-poem-packages", logfile="missing_file.log", age=2,
            timeout=10
        )

    def tearDown(self):
        for logfile in [
            self.logfile, self.logfile_wrong_format1,
            self.logfile_wrong_format2, self.logfile_wrong_format3,
            self.logfile_with_warn, self.logfile_with_error,
            self.logfile_with_recovery
        ]:
            if os.path.exists(logfile):
                os.remove(logfile)

    def test_compare_datetime(self):
        datetime1 = datetime.datetime(2022, 8, 1, 10, 0, 44)
        datetime2 = datetime.datetime(2022, 8, 1, 12, 0, 0)
        datetime3 = datetime.datetime(2022, 8, 1, 13, 5, 30)

        self.assertEqual(_compare_datetimes(datetime2, datetime1), 1)
        self.assertEqual(_compare_datetimes(datetime3, datetime1), 3)

    @patch("argo_probe_argo_tools.log._compare_datetimes")
    def test_log_ok(self, mock_compare):
        mock_compare.return_value = 1
        self.assertTrue(self.log.check_file_exists())
        msg = self.log.check_messages()
        self.assertEqual(msg, "The run finished successfully.")

    @patch("argo_probe_argo_tools.log._compare_datetimes")
    def test_log_ok_with_dash(self, mock_compare):
        mock_compare.return_value = 1
        with open(self.logfile, "w") as f:
            f.write(mock_ok_log_with_dash_in_msg)
        log = Log(
            app="argo-poem-packages", logfile=self.logfile, age=2, timeout=10
        )
        self.assertTrue(log.check_file_exists())
        msg = log.check_messages()
        self.assertEqual(msg, "The run finished - successfully.")

    @patch("argo_probe_argo_tools.log._compare_datetimes")
    def test_log_older_than_age(self, mock_compare):
        mock_compare.return_value = 3
        self.assertTrue(self.log.check_file_exists())
        with self.assertRaises(CriticalException) as context:
            self.log.check_messages()
        self.assertEqual(
            context.exception.__str__(),
            "argo-poem-packages not run in the past 2 hours"
        )

    def test_log_file_not_found(self):
        self.assertFalse(self.log_missing_file.check_file_exists())

    def test_log_file_wrong_format(self):
        with open(self.logfile_wrong_format1, "w") as f:
            f.write(mock_wrong_format1)

        with open(self.logfile_wrong_format2, "w") as f:
            f.write(mock_wrong_format2)

        with open(self.logfile_wrong_format3, "w") as f:
            f.write(mock_wrong_format3)

        log1 = Log(
            app="argo-poem-packages", logfile=self.logfile_wrong_format1, age=2,
            timeout=10
        )
        log2 = Log(
            app="argo-poem-packages", logfile=self.logfile_wrong_format2, age=2,
            timeout=10
        )
        log3 = Log(
            app="argo-poem-packages", logfile=self.logfile_wrong_format3, age=2,
            timeout=10
        )

        self.assertFalse(log1.check_format_ok())
        self.assertFalse(log2.check_format_ok())
        self.assertFalse(log3.check_format_ok())

    @patch("argo_probe_argo_tools.log._compare_datetimes")
    def test_log_with_warn(self, mock_compare):
        mock_compare.return_value = 1
        with open(self.logfile_with_warn, "w") as f:
            f.write(mock_log_with_warn)

        log = Log(
            app="argo-poem-packages", logfile=self.logfile_with_warn, age=2,
            timeout=10
        )

        with self.assertRaises(WarnException) as context:
            log.check_messages()

        self.assertEqual(
            context.exception.__str__(),
            "Packages not found with requested version: "
            "nagios-plugins-grycap-im-0.1.3"
        )

    @patch("argo_probe_argo_tools.log._compare_datetimes")
    def test_log_with_error(self, mock_compare):
        mock_compare.return_value = 1
        with open(self.logfile_with_error, "w") as f:
            f.write(mock_log_with_error)

        log = Log(
            app="argo-poem-packages", logfile=self.logfile_with_error, age=2,
            timeout=10
        )

        with self.assertRaises(CriticalException) as context:
            log.check_messages()

        self.assertEqual(
            context.exception.__str__(),
            "Error installing packages: Command '['yum', 'list', 'available', "
            "'--showduplicates']' returned non-zero exit status 1."
        )

    @patch("argo_probe_argo_tools.log._compare_datetimes")
    def test_log_with_recovery(self, mock_compare):
        mock_compare.return_value = 1
        with open(self.logfile_with_recovery, "w") as f:
            f.write(mock_log_recovered)

        log = Log(
            app="argo-poem-packages", logfile=self.logfile_with_recovery, age=2,
            timeout=10
        )

        msg = log.check_messages()
        self.assertEqual(msg, "The run finished successfully.")
