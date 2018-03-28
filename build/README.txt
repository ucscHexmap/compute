Use these scripts to build the python environment. The localy python should
only be needed once while the pyenv is built upon each change in python
libraries or versions.

Order of execution:

localpy <install-dir>
Build a local python which is specific to system libs already installed.
<install-dir> a full path to the python install directory.
You may need to install openssl if you get a warning that it is missing.

rm-localpy <install-dir>
Remove a local python install if needed to clean up a bad install.
<install-dir> a full path to the python install directory.

pyenv <config-file> <localpy-bin-dir>
Build a python virtual environment for this project.
<config-file> should be the full path to your config file in compute/config.
<localpy-bin-dir> the full path to the localpy bin dir.

--------------------------------------------------------------

MACOS NOTES:
Install some critical tools before you do anything else.
for MacOS 10.12.6 Sierra:
- install macPorts from:
    https://github.com/macports/macports-base/releases/download/v2.4.2/MacPorts-2.4.2-10.12-Sierra.pkg
- use root to install the libraries since some files require root access:
    su root
    port install wget
    port install openssl
