# argo-probe-poem-tools

The package contains four probes: 

* `check_dirsize.sh` - probe determines the size of a directory (including subdirectories) and compares it with the supplied thresholds.
* `check_file` - probe is checking given file's properties;
* `check_log` - probe is inspecting the application log file for errors;
* `parse_file` - probe is inspecting file for content and checking its age.

## Synopsis

### `check_dirsize.sh` probe

The probe determines the size of a directory (including subdirectories) and compares it with the supplied thresholds (must be defined in KB). It prints the size of the directory in KB followed by "ok" or either "warning" or "critical" if the corresponding threshold is reached.

Example execution of the probe:

```
/usr/libexec/argo/probes/argo_tools/check_dirsize.sh -d /var/spool/ams-publisher -w 10000 -c 100000 -f
OK - /var/spool/ams-publisher size: 732 KB|'size'=732KB;10000;100000
```

### `check_file` probe

The probe checks file properties for the given file. By default, it only checks if the file exists. Optionally, it can check if the file is one of the four types: plain file, directory, socket, or named pipe. Additionally, it is possible to check if file owner or group match the given values. It can also check if file is readable, writable, or executable by user and/or group.

Only mandatory argument is the file path, all the others are optional and except for file types, can be used in any combination.

```
# /usr/libexec/argo/probes/argo_tools/check_file -h
usage: check_file [-h] -F FILE [-f|-d|-s|-p] [-o OWNER] [-g GROUP] [-r] [-w] [-x] [-t TIMEOUT]

ARGO probe that checks file properties; by default, it checks only if it exists

required:
  -F FILE, --file FILE  file to check

optional:
  -f                    is it a plain file
  -d                    is it a directory
  -s                    is it a socket
  -p                    is it a named pipe
  -o OWNER, --owner OWNER
                        is the file owner matching the one given
  -g GROUP, --group GROUP
                        is the file group matching the one given
  -r                    is it user-or-group readable
  -w                    is it user-or-group writable
  -x                    is it user-or-group executable
  -t TIMEOUT, --timeout TIMEOUT
                        time in seconds after which the probe will stop execution and return CRITICAL (default: 10)
  -h, --help            Show this help message and exit
```

Example execution of the probe (checking if the file is plain file and writable):

```
# /usr/libexec/argo/probes/argo_tools/check_file -F <PATH-TO-FILE> -f -w -t 20
OK - File OK
```

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

### `parse_file` probe

The probe is checking the given file for its modification time - it must be modified less than `<TIME>` hours ago for the probe to return OK. It is also checking if the file contains a `<STRING>` - if it does not, the probe returns CRITICAL.

Mandatory arguments are `<FILE>`, `<TIME>` and `<STRING>`, whereas `<TIMEOUT>` argument has a default value defined.

```
/usr/libexec/argo/probes/argo_tools/parse_file -h
usage: parse_file [-h] -f FILE -T TIME -s STRING [-t TIMEOUT]

ARGO probe that checks text file age and content; it raises critical status if file age is greater than maximum acceptable age or the requested content is not found in the file

required arguments:
  -f FILE, --file FILE  Location of file being checked
  -T TIME, --time TIME  Maximum acceptable time (in hours) since file was last modified
  -s STRING, --string STRING
                        The string which must exist in the file if the probe is to return OK status

optional arguments:
  -t TIMEOUT, --timeout TIMEOUT
                        Time in seconds after which the probe will stop execution and return CRITICAL (default: 10)
  -h, --help            Show this help message and exit
```

Example execution of the probe:

```
/usr/libexec/argo/probes/argo_tools/parse_file -f /var/log/ncg.log -T 2 -s "No serious problems were detected during the pre-flight check" -t 30
OK - File is OK
```
