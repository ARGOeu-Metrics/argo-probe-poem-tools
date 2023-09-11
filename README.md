# argo-probe-poem-tools

The package contains two probes: 

* `check_log` - probe is inspecting the application log file for errors;
* `check_file` - probe is inspecting file for content and checking its age.

## Synopsis

### `check_log` probe

The probe reports if the application has not been executed in the given time, and raises critical and warning statuses in case there are error or warning messages in the log respectively.

Mandatory arguments are `<FILE>` and `<APP>`, while `<AGE>` and `<TIMEOUT>` have default values defined.

```
# /usr/libexec/argo/probes/argo_tools/check_log -h
usage: check_log -f FILE -A APP [-a AGE] [-t TIMEOUT] [-h]

Nagios probe checking logfile messages

required arguments:
  -f FILE, --file FILE  location of log file
  -A APP, --app APP     application whose log is being checked

optional arguments:
  -a AGE, --age AGE     maximum acceptable log age (default: 2 h)
  -t TIMEOUT, --timeout TIMEOUT
                        timeout (default 90 s)
  -h, --help            Show this help message and exit
```

Example execution of the probe:

```
# /usr/libexec/argo/probes/argo_tools/check_log -f /var/log/argo-poem-tools/argo-poem-tools.log -A argo-poem-packages -m finished -a 2 -t 90
OK - The run finished successfully.
```

### `check_file` probe

The probe is checking the given file for its modification time - it must be modified less than `<TIME>` hours ago for the probe to return OK. It is also checking if the file contains a `<STRING>` - if it does not, the probe returns CRITICAL.

Mandatory arguments are `<FILE>`, `<TIME>` and `<STRING>`, whereas `<TIMEOUT>` argument has a default value defined.

```
/usr/libexec/argo/probes/argo_tools/check_file -h
usage: check_file [-h] -f FILE -T TIME -s STRING [-t TIMEOUT]

Nagios probe for checking file age and content; it raises critical status if
file age is greater than maximum acceptable age or the requested content is
not found in the file

required arguments:
  -f FILE, --file FILE  Location of file being checked
  -T TIME, --time TIME  Maximum acceptable time (in hours) since file was last
                        modified
  -s STRING, --string STRING
                        The string which must exist in the file if the probe
                        is to return OK status

optional arguments:
  -t TIMEOUT, --timeout TIMEOUT
                        Time in seconds after which the probe will stop
                        execution and return CRITICAL (default: 10)
  -h, --help            Show this help message and exit
```

Example execution of the probe:

```
/usr/libexec/argo/probes/argo_tools/check_file -f /var/log/ncg.log -T 2 -s "No serious problems were detected during the pre-flight check" -t 30
OK - File is OK
```
