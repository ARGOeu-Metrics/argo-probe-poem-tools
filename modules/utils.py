import os


def does_file_exist(filename):
    if os.path.exists(filename) and os.path.isfile(filename):
        return True

    else:
        return False


class WarnException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class CriticalException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
