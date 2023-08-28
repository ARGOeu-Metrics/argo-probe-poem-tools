from argo_probe_argo_tools.utils import does_file_exist


class File:
    def __init__(self, filename, timeout):
        self.filename = filename
        self.timeout = timeout

    def _read(self):
        with open(self.filename, "r") as f:
            data = [line for line in f.readlines()]

        return data

    def check_existence(self):
        return does_file_exist(self.filename)
