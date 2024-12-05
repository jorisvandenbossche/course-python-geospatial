# This script is adapted from Andreas Mueller:
# https://github.com/amueller/scipy-2018-sklearn/blob/master/check_env.ipynb
# and glemaitre: https://github.com/glemaitre/pyparis-2018-sklearn/blob/master/check_environment.py

import sys


# packaging is not in the stdlib, but should be available as dependency of
# some other package (eg jupyterlab, geopandas, ..)
from packaging import version

try:
    import curses
    curses.setupterm()
    assert curses.tigetnum("colors") > 2
    OK = "\x1b[1;%dm[ OK ]\x1b[0m" % (30 + curses.COLOR_GREEN)
    FAIL = "\x1b[1;%dm[FAIL]\x1b[0m" % (30 + curses.COLOR_RED)
except:
    OK = '[ OK ]'
    FAIL = '[FAIL]'

try:
    import importlib
except ImportError:
    print(FAIL, "Python version 3.4 is required,"
                " but %s is installed." % sys.version)


def import_version(pkg, min_ver, fail_msg=""):
    mod = None
    try:
        mod = importlib.import_module(pkg)
        if min_ver:
            ver = mod.__version__
            if version.parse(ver) < version.parse(min_ver):
                print(FAIL, "%s version %s or higher required, but %s installed."
                    % (lib, min_ver, ver))
            else:
                print(OK, '%s version %s' % (pkg, ver))
        else:
            print(OK, f"{pkg}")
    except ImportError:
        print(FAIL, '%s not installed. %s' % (pkg, fail_msg))
    return mod


# first check the python version
print('Using python in', sys.prefix)
print(sys.version)
pyversion = version.parse(sys.version.split(" ")[0])
if pyversion >= version.parse("3"):
    if pyversion < version.parse("3.10"):
        print(FAIL, "Python version 3.10 is required,"
                    " but %s is installed." % sys.version)
else:
    print(FAIL, "Python 3 is required, but %s is installed." % sys.version)

print()
requirements = {'numpy': "1.9", 'matplotlib': "2.0",
                'pandas': "2.0", 'xarray': '0.16',
                'geopandas': '1.0', 'rasterio': '1.1',
                'owslib': '0.19', 'fsspec': '0.8',
                's3fs': '0.3', 'pyproj': '2.4',
                'hvplot.xarray': None}

# now the dependencies
for lib, required_version in list(requirements.items()):
    import_version(lib, required_version)
