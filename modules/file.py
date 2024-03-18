import datetime
import math
import os
import stat

from argo_probe_argo_tools.utils import CriticalException


def now_epoch():
    return datetime.datetime.now().timestamp()


class File:
    def __init__(self, filename):
        self.filename = filename
        try:
            self.mode = os.lstat(self.filename).st_mode

        except FileNotFoundError as e:
            raise CriticalException(str(e))

    def _read(self):
        with open(self.filename, "r") as f:
            data = [line for line in f.readlines()]

        return "\n".join(data)

    def _exist(self):
        return os.path.exists(self.filename)

    def is_file(self):
        return os.path.isfile(self.filename)

    def is_directory(self):
        return stat.S_ISDIR(self.mode)

    def is_socket(self):
        return stat.S_ISSOCK(self.mode)

    def is_fifo(self):
        return stat.S_ISFIFO(self.mode)

    def _get_file_age(self):
        return os.path.getmtime(self.filename)

    def check_age(self, age):
        hours_since_modified = math.floor(
            (now_epoch() - self._get_file_age()) / 3600.
        )

        if hours_since_modified > age:
            raise CriticalException(
                f"File {self.filename} last modified {hours_since_modified} "
                f"hours ago"
            )

    def check_content(self, string):
        content = self._read()

        if string not in content:
            raise CriticalException(
                f"File {self.filename} does not contain '{string}' string"
            )
