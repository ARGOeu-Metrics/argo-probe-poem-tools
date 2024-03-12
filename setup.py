import glob
from distutils.core import setup

NAME = "argo-probe-argo-tools"


def get_ver():
    try:
        for line in open(NAME + '.spec'):
            if "Version:" in line:
                return line.split()[1]

    except IOError:
        raise SystemExit(1)


setup(
    name=NAME,
    version=get_ver(),
    author="SRCE",
    author_email="kzailac@srce.hr",
    description="ARGO probe that inspects the application log file for errors",
    url="https://github.com/ARGOeu-Metrics/argo-probe-argo-tools",
    package_dir={'argo_probe_argo_tools': 'modules'},
    packages=['argo_probe_argo_tools'],
    data_files=[
        ('/usr/libexec/argo/probes/argo_tools', glob.glob("src/*"))
    ]
)
