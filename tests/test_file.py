import datetime
import os
import socket
import unittest
from unittest.mock import patch

from argo_probe_argo_tools.file import File
from argo_probe_argo_tools.utils import CriticalException

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
        self.directory = "mock_directory"
        self.socket_name = "mock_socket"
        self.fifo = "mock_fifo"

        with open(self.filename, "w") as f:
            f.write(mock_file_content)

        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.bind(self.socket_name)

        except OSError:
            pass

        try:
            os.mkfifo(self.fifo)

        except OSError:
            pass

        self.filecheck = File(filename=self.filename)
        self.dircheck = File(filename=self.directory)
        self.socketcheck = File(filename=self.socket_name)
        self.fifocheck = File(filename=self.fifo)

    def tearDown(self) -> None:
        if os.path.exists(self.filename):
            os.remove(self.filename)

        if os.path.exists(self.directory):
            os.rmdir(self.directory)

        self.socket.close()

        if os.path.exists(self.socket_name):
            os.remove(self.socket_name)

        if os.path.exists(self.fifo):
            os.remove(self.fifo)

    def test_nonexisting(self):
        with self.assertRaises(CriticalException) as context:
            File(filename="nonexisting")
        self.assertEqual(
            context.exception.__str__(),
            "[Errno 2] No such file or directory: 'nonexisting'"
        )

    def test_is_file(self):
        self.assertTrue(self.filecheck.is_file())
        self.assertFalse(self.dircheck.is_file())
        self.assertFalse(self.socketcheck.is_file())
        self.assertFalse(self.fifocheck.is_file())

    def test_is_directory(self):
        self.assertFalse(self.filecheck.is_directory())
        self.assertTrue(self.dircheck.is_directory())
        self.assertFalse(self.socketcheck.is_directory())
        self.assertFalse(self.fifocheck.is_directory())

    def test_is_socket(self):
        self.assertFalse(self.filecheck.is_socket())
        self.assertFalse(self.dircheck.is_socket())
        self.assertTrue(self.socketcheck.is_socket())
        self.assertFalse(self.fifocheck.is_socket())

    def test_is_fifo(self):
        self.assertFalse(self.filecheck.is_fifo())
        self.assertFalse(self.dircheck.is_fifo())
        self.assertFalse(self.socketcheck.is_fifo())
        self.assertTrue(self.fifocheck.is_fifo())

    @patch("argo_probe_argo_tools.file.pathlib.Path.owner")
    def test_check_owner(self, mock_owner):
        mock_owner.return_value = "test"
        self.assertTrue(self.filecheck.check_owner("test"))
        self.assertFalse(self.filecheck.check_owner("sensu"))
        self.assertTrue(self.dircheck.check_owner("test"))
        self.assertFalse(self.dircheck.check_owner("sensu"))
        self.assertTrue(self.socketcheck.check_owner("test"))
        self.assertFalse(self.socketcheck.check_owner("sensu"))
        self.assertTrue(self.fifocheck.check_owner("test"))
        self.assertFalse(self.fifocheck.check_owner("sensu"))

    @patch("argo_probe_argo_tools.file.pathlib.Path.group")
    def test_check_group(self, mock_group):
        mock_group.return_value = "test"
        self.assertTrue(self.filecheck.check_group("test"))
        self.assertFalse(self.filecheck.check_group("sensu"))
        self.assertTrue(self.dircheck.check_group("test"))
        self.assertFalse(self.dircheck.check_group("sensu"))
        self.assertTrue(self.socketcheck.check_group("test"))
        self.assertFalse(self.socketcheck.check_group("sensu"))
        self.assertTrue(self.fifocheck.check_group("test"))
        self.assertFalse(self.fifocheck.check_group("sensu"))

    @patch("argo_probe_argo_tools.file.now_epoch")
    def test_age(self, mock_now):
        mock_now.return_value = (
                datetime.datetime.now() + datetime.timedelta(hours=4)
        ).timestamp()

        self.filecheck.check_age(age=4)

        with self.assertRaises(CriticalException) as context:
            self.filecheck.check_age(age=3)

        self.assertEqual(
            context.exception.__str__(),
            "File mock_file.log last modified 4 hours ago"
        )

    def test_content(self):
        self.filecheck.check_content("No serious problems were detected")

        with self.assertRaises(CriticalException) as context:
            self.filecheck.check_content("Nonexisting content")

        self.assertEqual(
            context.exception.__str__(),
            "File mock_file.log does not contain 'Nonexisting content' string"
        )
