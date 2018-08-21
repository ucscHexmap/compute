Use these scripts to build the python environment. localpy should be needed once
per pyenv build due to library or version changes.

Order of execution:

localpy <install-dir>
Build a local python which is specific to system libs already installed.
<install-dir> a full path to the python install directory.
You may need to install openssl if you get a warning that it is missing.

rm-localpy <install-dir>
Remove a local python install if needed to clean up a bad install.
<install-dir> a full path to the python install directory.

pyenv
Build a python virtual environment for this project.

--------------------------------------------------------------

MACOS NOTES:
Install wget and openssl before you do anything else.
for MacOS 10.12.6 Sierra:
- install macPorts from:
    https://github.com/macports/macports-base/releases/download/v2.4.2/MacPorts-2.4.2-10.12-Sierra.pkg
- use root to install the libraries since some files require root access:
    su root
    port install wget
    port install openssl
