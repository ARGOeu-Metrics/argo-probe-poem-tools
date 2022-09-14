import unittest

from argo_probe_argo_tools.nagios import Nagios


class NagiosTests(unittest.TestCase):
    def setUp(self):
        self.nagios = Nagios()

    def test_ok(self):
        self.nagios.ok("Everything is ok")
        self.assertEqual(self.nagios.get_msg(), "OK - Everything is ok")
        self.assertEqual(self.nagios.get_code(), 0)

    def test_warning(self):
        self.nagios.warning("This is the final warning")
        self.assertEqual(
            self.nagios.get_msg(), "WARNING - This is the final warning"
        )
        self.assertEqual(self.nagios.get_code(), 1)

    def test_critical(self):
        self.nagios.critical("Something is wrong")
        self.assertEqual(self.nagios.get_msg(), "CRITICAL - Something is wrong")
        self.assertEqual(self.nagios.get_code(), 2)

    def test_unknown(self):
        self.nagios.unknown("I don't know what is happening")
        self.assertEqual(
            self.nagios.get_msg(), "UNKNOWN - I don't know what is happening"
        )
        self.assertEqual(self.nagios.get_code(), 3)
