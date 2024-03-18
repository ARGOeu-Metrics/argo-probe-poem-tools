import datetime
import os
import socket
import unittest
from unittest.mock import patch

from argo_probe_argo_tools.file import File, TextFile
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
        self.filename = "mock_file"
        self.directory = "mock_directory"
        self.socket_name = "mock_socket"
        self.fifo = "mock_fifo"
        self.filename2 = "mock_file"
        self.directory2 = "mock_directory2"
        self.socket_name2 = "mock_socket2"
        self.fifo2 = "mock_fifo2"

        with open(self.filename, "w"):
            pass

        with open(self.filename2, "w"):
            pass

        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

        if not os.path.exists(self.directory2):
            os.mkdir(self.directory2)

        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.bind(self.socket_name)

            self.socket2 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket2.bind(self.socket_name2)

        except OSError:
            pass

        try:
            os.mkfifo(self.fifo)
            os.mkfifo(self.fifo2)

        except OSError:
            pass

        self.filecheck = File(filename=self.filename)
        self.dircheck = File(filename=self.directory)
        self.socketcheck = File(filename=self.socket_name)
        self.fifocheck = File(filename=self.fifo)

    def tearDown(self) -> None:
        if os.path.exists(self.filename):
            os.remove(self.filename)

        if os.path.exists(self.filename2):
            os.remove(self.filename2)

        if os.path.exists(self.directory):
            os.rmdir(self.directory)

        if os.path.exists(self.directory2):
            os.rmdir(self.directory2)

        self.socket.close()
        self.socket2.close()

        if os.path.exists(self.socket_name):
            os.remove(self.socket_name)

        if os.path.exists(self.socket_name2):
            os.remove(self.socket_name2)

        if os.path.exists(self.fifo):
            os.remove(self.fifo)

        if os.path.exists(self.fifo2):
            os.remove(self.fifo2)

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

    def test_is_readable_by_user_and_not_group(self):
        os.chmod(self.filename2, 0o400)
        os.chmod(self.directory2, 0o400)
        os.chmod(self.socket_name2, 0o400)
        os.chmod(self.fifo2, 0o400)
        file = File(filename=self.filename2)
        directory = File(filename=self.directory2)
        fsocket = File(filename=self.socket_name2)
        fifo = File(filename=self.fifo2)
        self.assertTrue(file.is_readable())
        self.assertTrue(directory.is_readable())
        self.assertTrue(fsocket.is_readable())
        self.assertTrue(fifo.is_readable())

    def test_is_readable_by_group_and_not_user(self):
        os.chmod(self.filename2, 0o140)
        os.chmod(self.directory2, 0o140)
        os.chmod(self.socket_name2, 0o140)
        os.chmod(self.fifo2, 0o140)
        file = File(filename=self.filename2)
        directory = File(filename=self.directory2)
        fsocket = File(filename=self.socket_name2)
        fifo = File(filename=self.fifo2)
        self.assertTrue(file.is_readable())
        self.assertTrue(directory.is_readable())
        self.assertTrue(fsocket.is_readable())
        self.assertTrue(fifo.is_readable())

    def test_is_readable_by_both_user_and_group(self):
        os.chmod(self.filename2, 0o440)
        os.chmod(self.directory2, 0o440)
        os.chmod(self.socket_name2, 0o440)
        os.chmod(self.fifo2, 0o440)
        file = File(filename=self.filename2)
        directory = File(filename=self.directory2)
        fsocket = File(filename=self.socket_name2)
        fifo = File(filename=self.fifo2)
        self.assertTrue(file.is_readable())
        self.assertTrue(directory.is_readable())
        self.assertTrue(fsocket.is_readable())
        self.assertTrue(fifo.is_readable())

    def test_not_readable_by_anyone(self):
        os.chmod(self.filename2, 0o100)
        os.chmod(self.directory2, 0o100)
        os.chmod(self.socket_name2, 0o100)
        os.chmod(self.fifo2, 0o100)
        file = File(filename=self.filename2)
        directory = File(filename=self.directory2)
        fsocket = File(filename=self.socket_name2)
        fifo = File(filename=self.fifo2)
        self.assertFalse(file.is_readable())
        self.assertFalse(directory.is_readable())
        self.assertFalse(fsocket.is_readable())
        self.assertFalse(fifo.is_readable())

    def test_is_writable_by_user_and_not_group(self):
        os.chmod(self.filename2, 0o200)
        os.chmod(self.directory2, 0o200)
        os.chmod(self.socket_name2, 0o200)
        os.chmod(self.fifo2, 0o200)
        file = File(filename=self.filename2)
        directory = File(filename=self.directory2)
        fsocket = File(filename=self.socket_name2)
        fifo = File(filename=self.fifo2)
        self.assertTrue(file.is_writable())
        self.assertTrue(directory.is_writable())
        self.assertTrue(fsocket.is_writable())
        self.assertTrue(fifo.is_writable())

    def test_is_writable_by_group_and_not_user(self):
        os.chmod(self.filename2, 0o120)
        os.chmod(self.directory2, 0o120)
        os.chmod(self.socket_name2, 0o120)
        os.chmod(self.fifo2, 0o120)
        file = File(filename=self.filename2)
        directory = File(filename=self.directory2)
        fsocket = File(filename=self.socket_name2)
        fifo = File(filename=self.fifo2)
        self.assertTrue(file.is_writable())
        self.assertTrue(directory.is_writable())
        self.assertTrue(fsocket.is_writable())
        self.assertTrue(fifo.is_writable())

    def test_is_writable_by_both_user_and_group(self):
        os.chmod(self.filename2, 0o220)
        os.chmod(self.directory2, 0o220)
        os.chmod(self.socket_name2, 0o220)
        os.chmod(self.fifo2, 0o220)
        file = File(filename=self.filename2)
        directory = File(filename=self.directory2)
        fsocket = File(filename=self.socket_name2)
        fifo = File(filename=self.fifo2)
        self.assertTrue(file.is_writable())
        self.assertTrue(directory.is_writable())
        self.assertTrue(fsocket.is_writable())
        self.assertTrue(fifo.is_writable())

    def test_not_writable_by_anyone(self):
        os.chmod(self.filename2, 0o100)
        os.chmod(self.directory2, 0o100)
        os.chmod(self.socket_name2, 0o100)
        os.chmod(self.fifo2, 0o100)
        file = File(filename=self.filename2)
        directory = File(filename=self.directory2)
        fsocket = File(filename=self.socket_name2)
        fifo = File(filename=self.fifo2)
        self.assertFalse(file.is_writable())
        self.assertFalse(directory.is_writable())
        self.assertFalse(fsocket.is_writable())
        self.assertFalse(fifo.is_writable())

    def test_is_executable_by_user_and_not_group(self):
        os.chmod(self.filename2, 0o100)
        os.chmod(self.directory2, 0o100)
        os.chmod(self.socket_name2, 0o100)
        os.chmod(self.fifo2, 0o100)
        file = File(filename=self.filename2)
        directory = File(filename=self.directory2)
        fsocket = File(filename=self.socket_name2)
        fifo = File(filename=self.fifo2)
        self.assertTrue(file.is_executable())
        self.assertTrue(directory.is_executable())
        self.assertTrue(fsocket.is_executable())
        self.assertTrue(fifo.is_executable())

    def test_is_executable_by_group_and_not_user(self):
        os.chmod(self.filename2, 0o010)
        os.chmod(self.directory2, 0o010)
        os.chmod(self.socket_name2, 0o010)
        os.chmod(self.fifo2, 0o010)
        file = File(filename=self.filename2)
        directory = File(filename=self.directory2)
        fsocket = File(filename=self.socket_name2)
        fifo = File(filename=self.fifo2)
        self.assertTrue(file.is_executable())
        self.assertTrue(directory.is_executable())
        self.assertTrue(fsocket.is_executable())
        self.assertTrue(fifo.is_executable())

    def test_is_executable_by_both_user_and_group(self):
        os.chmod(self.filename2, 0o540)
        os.chmod(self.directory2, 0o540)
        os.chmod(self.socket_name2, 0o540)
        os.chmod(self.fifo2, 0o540)
        file = File(filename=self.filename2)
        directory = File(filename=self.directory2)
        fsocket = File(filename=self.socket_name2)
        fifo = File(filename=self.fifo2)
        self.assertTrue(file.is_executable())
        self.assertTrue(directory.is_executable())
        self.assertTrue(fsocket.is_executable())
        self.assertTrue(fifo.is_executable())

    def test_not_executable_by_anyone(self):
        os.chmod(self.filename2, 0o400)
        os.chmod(self.directory2, 0o400)
        os.chmod(self.socket_name2, 0o400)
        os.chmod(self.fifo2, 0o400)
        file = File(filename=self.filename2)
        directory = File(filename=self.directory2)
        fsocket = File(filename=self.socket_name2)
        fifo = File(filename=self.fifo2)
        self.assertFalse(file.is_executable())
        self.assertFalse(directory.is_executable())
        self.assertFalse(fsocket.is_executable())
        self.assertFalse(fifo.is_executable())


class TextFileTests(unittest.TestCase):
    def setUp(self):
        self.filename = "mock_file"
        with open(self.filename, "w") as f:
            f.write(mock_file_content)

        self.parse = TextFile(filename=self.filename)

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    @patch("argo_probe_argo_tools.file.now_epoch")
    def test_age(self, mock_now):
        mock_now.return_value = (
                datetime.datetime.now() + datetime.timedelta(hours=4)
        ).timestamp()

        self.parse.check_age(age=4)

        with self.assertRaises(CriticalException) as context:
            self.parse.check_age(age=3)

        self.assertEqual(
            context.exception.__str__(),
            "File mock_file last modified 4 hours ago"
        )

    def test_content(self):
        self.parse.check_content("No serious problems were detected")

        with self.assertRaises(CriticalException) as context:
            self.parse.check_content("Nonexisting content")

        self.assertEqual(
            context.exception.__str__(),
            "File mock_file does not contain 'Nonexisting content' string"
        )
