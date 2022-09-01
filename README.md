# argo-probe-poem-tools

Probe inspecting the execution of argo-poem-tools. The probe reports if the tool has not been executed in the given time, and raises critical and warning statuses in case there are error or warning messages in the log respectively.

## Synopsis

The probe has three mandatory arguments: log file location, acceptable maximum log age, and timeout.

```
# /usr/libexec/argo/probes/poem_tools/check_log -h
usage: Probe that checks argo-poem-tools execution [-f FILE] [-a AGE]
                                                   [-t TIMEOUT] [-h]

required arguments:
  -f FILE, --file FILE  argo-poem-tools log file (default: /var/log/argo-poem-
                        tools/argo-poem-tools.log)
  -a AGE, --age AGE     maximum acceptable log age (default: 2 h)
  -t TIMEOUT, --timeout TIMEOUT
                        timeout

optional arguments:
  -h, --help            Show this help message and exit
```

Example execution of the probe:

```
# /usr/libexec/argo/probes/poem_tools/check_log -f /var/log/argo-poem-tools/argo-poem-tools.log -a 2 -t 90
OK - The run finished successfully.
```
