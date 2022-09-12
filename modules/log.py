import datetime
import os
import time


def _compare_datetimes(datetime1, datetime2):
    return divmod((datetime1 - datetime2).total_seconds(), 3600)[0]


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


class Log:
    def __init__(self, logfile, age, timeout):
        self.logfile = logfile
        self.age = age
        self.timeout = datetime.timedelta(seconds=timeout)

    def check_file_exists(self):
        if os.path.exists(self.logfile) and os.path.isfile(self.logfile):
            return True

        else:
            return False

    def _read(self):
        data = list()
        with open(self.logfile, "r") as f:
            lines = [line for line in f.readlines() if line.strip()]
            for line in lines[-20:]:
                entries = line.split(" - ")
                data.append(
                    {
                        "datetime": datetime.datetime.strptime(
                            entries[0].strip(), "%Y-%m-%d %H:%M:%S"
                        ),
                        "app": entries[1].strip(),
                        "level": entries[2].strip(),
                        "msg": " - ".join(entries[3:]).strip()
                    }
                )

        return data

    def check_format_ok(self):
        format_ok = True

        try:
            data = self._read()

            apps = set([item["app"] for item in data])
            if not (len(apps) == 1 and "argo-poem-packages" in apps):
                format_ok = False

            levels = set([item["level"] for item in data])
            permitted_levels = {
                "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"
            }
            if len(levels.difference(permitted_levels)) > 0:
                format_ok = False

        except ValueError:
            format_ok = False

        return format_ok

    def check_messages(self):
        t = datetime.datetime.now()
        while datetime.datetime.now() - t < self.timeout:
            data = self._read()

            younger_than_age = [
                item for item in data if
                _compare_datetimes(datetime.datetime.now(), item["datetime"]) <
                self.age
            ]

            warn_msgs = [
                item["msg"] for item in younger_than_age if
                item["level"] == "WARNING"
            ]

            crit_msgs = [
                item["msg"] for item in younger_than_age if
                item["level"] in ["CRITICAL", "ERROR"]
            ]

            if len(younger_than_age) > 0:
                if "finished" in younger_than_age[-1]["msg"]:
                    return f"{younger_than_age[-1]['msg']}"

                elif len(crit_msgs) > 0:
                    raise CriticalException("\n".join(crit_msgs))

                elif len(warn_msgs) > 0:
                    raise WarnException("\n".join(warn_msgs))

                else:
                    time.sleep(30)
                    continue

            else:
                raise CriticalException(
                    f"argo-poem-packages not run in the past {self.age} hours"
                )

        else:
            raise TimeoutError
