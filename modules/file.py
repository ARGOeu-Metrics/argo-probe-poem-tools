import datetime
import math
import os

from argo_probe_argo_tools.utils import does_file_exist, CriticalException


def now_epoch():
    return datetime.datetime.now().timestamp()


class File:
    def __init__(self, filename):
        self.filename = filename

    def _read(self):
        with open(self.filename, "r") as f:
            data = [line for line in f.readlines()]

        return "\n".join(data)

    def check_existence(self):
        return does_file_exist(self.filename)

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
