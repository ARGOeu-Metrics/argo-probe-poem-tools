class Status:
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3

    def __init__(self):
        self._code = self.OK
        self._msg = ""

    def ok(self, msg):
        self._msg = f"OK - {msg}"
        self._code = self.OK

    def warning(self, msg):
        self._msg = f"WARNING - {msg}"
        self._code = self.WARNING

    def critical(self, msg):
        self._msg = f"CRITICAL - {msg}"
        self._code = self.CRITICAL

    def unknown(self, msg):
        self._msg = f"UNKNOWN - {msg}"
        self._code = self.UNKNOWN

    def get_code(self):
        return self._code

    def get_msg(self):
        return self._msg
