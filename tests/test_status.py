import unittest

from argo_probe_argo_tools.status import Status


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.status = Status()

    def test_ok(self):
        self.status.ok("Everything is ok")
        self.assertEqual(self.status.get_msg(), "OK - Everything is ok")
        self.assertEqual(self.status.get_code(), 0)

    def test_warning(self):
        self.status.warning("This is the final warning")
        self.assertEqual(
            self.status.get_msg(), "WARNING - This is the final warning"
        )
        self.assertEqual(self.status.get_code(), 1)

    def test_critical(self):
        self.status.critical("Something is wrong")
        self.assertEqual(self.status.get_msg(), "CRITICAL - Something is wrong")
        self.assertEqual(self.status.get_code(), 2)

    def test_unknown(self):
        self.status.unknown("I don't know what is happening")
        self.assertEqual(
            self.status.get_msg(), "UNKNOWN - I don't know what is happening"
        )
        self.assertEqual(self.status.get_code(), 3)
