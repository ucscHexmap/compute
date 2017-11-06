Use these scripts to build the python environment. The localy python should
only be needed once while the pyenv is built upon each change in python
libraries or versions.

Order of execution:

localpy <install-dir>
Build a local python install usable by multiple projects.
<install-dir> is optional, a full path to the python install directory,
defaults to $HOME/localpy.

rm-localpy <install-dir>
Remove a local python install if needed to clean up a bad install.
<install-dir> is optional, a full path to the python install directory,
defaults to $HOME/localpy.

pyenv <config-file>
Build a python virtual environment for this project.
<config-file> should be the full path to your config file in compute/config.

--------------------------------------------------------------

MACOS NOTES:
Install some critical tools before you do anything else.
for MacOS 10.12.6 Sierra:
- install macPorts: download the .pkg:
    https://github.com/macports/macports-base/releases/download/v2.4.2/MacPorts-2.4.2-10.12-Sierra.pkg
- double-click on the .pkg in a finder window to install
- use root to install the rest since some files require root access:
    su root
- install the xcode command line tools
    xcode-select --install
- install libraries
    port install wget
    port install openssl
