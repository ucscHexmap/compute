Use these scripts to build the python environment. localpy should be needed once
per pyenv build due to library or version changes.

Order of execution:

localpy <install-dir>
If you already have python v2 installed, skip to "pyenv".
Build a local python which is specific to system libs already installed.
<install-dir> a full path to the python install directory.
You may need to install openssl if you get a warning that it is missing.

rm-localpy <install-dir>
If needed to clean up a bad install, remove this local install with:
<install-dir> a full path to the python install directory.

pyenv
Build a python virtual environment for this project.

--------------------------------------------------------------

MACOS NOTES:
For python, pip and virtualenv installs, see localpy script.

