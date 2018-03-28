#!/usr/bin/env bash

pylint -rn *.py > lintout

echo "###############################" >> lintout
echo "pycodestle:" >> lintout

pycodestyle --first *.py >> lintout


echo "###############################" >> lintout
echo "pydocstyle: " >> lintout

pydocstyle *.py >> lintout

vim lintout

