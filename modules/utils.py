import os


def does_file_exist(filename):
    if os.path.exists(filename) and os.path.isfile(filename):
        return True

    else:
        return False
