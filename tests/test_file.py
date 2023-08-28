import os
import unittest

from argo_probe_argo_tools.file import File

mock_file_content = """
Checking objects...
        Checked 5511 services.
        Checked 1000 hosts.
        Checked 333 host groups.
        Checked 1579 service groups.
        Checked 729 contacts.
        Checked 220 contact groups.
        Checked 21 commands.
        Checked 1 time periods.
        Checked 0 host escalations.
        Checked 0 service escalations.
Checking for circular paths...
        Checked 1000 hosts
        Checked 0 service dependencies
        Checked 0 host dependencies
        Checked 1 timeperiods
Checking global event handlers...
Checking obsessive compulsive processor commands...
Checking misc settings...

Total Warnings: 0
Total Errors:   0

Things look okay - No serious problems were detected during the pre-flight check
Redirecting to /bin/systemctl restart nagios.service
"""


class FileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.filename = "mock_file.log"

        with open(self.filename, "w") as f:
            f.write(mock_file_content)

        self.filecheck = File(filename=self.filename, timeout=30)
        self.nonexisting_filecheck = File(filename="nonexisting", timeout=30)

    def tearDown(self) -> None:
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_file_existence(self):
        self.assertTrue(self.filecheck.check_existence())
        self.assertFalse(self.nonexisting_filecheck.check_existence())
