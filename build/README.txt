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

To modify only the PYTHONPATH of the virtual env, edit $PYENV/bin/activate to
replace the last line defining PYTHONPATH with the new path.

--------------------------------------------------------------

MACOS NOTES:
For python, pip and virtualenv installs, see localpy script.