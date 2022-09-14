# argo-probe-poem-tools

Probe inspecting the application log file for errors. The probe reports if the application has not been executed in the given time, and raises critical and warning statuses in case there are error or warning messages in the log respectively.

## Synopsis

The probe has five mandatory arguments: log file location, acceptable maximum log age, and timeout.

```
# /usr/libexec/argo/probes/argo_tools/check_log -h
usage: Probe that checks app log for errors [-f FILE] [-A APP] [-m MESSAGE]
                                            [-a AGE] [-t TIMEOUT] [-h]

required arguments:
  -f FILE, --file FILE  location of log file
  -A APP, --app APP     application whose log is being checked
  -m MESSAGE, --message MESSAGE
                        (part of) OK message expected in the log
  -a AGE, --age AGE     maximum acceptable log age (default: 2 h)
  -t TIMEOUT, --timeout TIMEOUT
                        timeout (default 90 s)

optional arguments:
  -h, --help            Show this help message and exit
```

Example execution of the probe:

```
# /usr/libexec/argo/probes/argo_tools/check_log -f /var/log/argo-poem-tools/argo-poem-tools.log -A argo-poem-packages -m finished -a 2 -t 90
OK - The run finished successfully.
```
