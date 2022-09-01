from distutils.core import setup


NAME = "argo-probe-poem-tools"


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
    description="ARGO probe that inspects the execution of argo-poem-tools",
    url="https://github.com/ARGOeu-Metrics/argo-probe-poem-tools",
    package_dir={'argo_probe_poem_tools': 'modules'},
    packages=['argo_probe_poem_tools'],
    data_files=[('/usr/libexec/argo/probes/poem_tools', ['src/check_log'])]
)
