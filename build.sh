#!/usr/bin/env bash

virtualenv --python python3.6 venv

source ./venv/bin/activate

pip install -r requirements.txt --extra-index-url $GEMFURY_URL

# minify all the files, leaving the output with a '.py.tmp' ending name
find lostservice -type f -name '*.py' -execdir pyminifier -o {}.pytmp {}  \;

# delete all of the .py source files
find lostservice -type f -not -name '*.pytmp' -delete

# rename the minified '.pytmp' files to be their original module names
find lostservice -type f -name '*.pytmp' -execdir rename 's/.py.pytmp/.py/' {} \;

# generate bytecode
python -m compileall lostservice

# delete all of the .py source files again
find lostservice -type f -not -name '*.pyc' -a -not -name '*.pyo' -delete

# move the .pyc files out of the __pycache__ directory to where the source files were
find lostservice -type f -name '*.pyc' -execdir mv {} .. \;

# rename the source files to be their original module names
find lostservice -type f -name '*.pyc' -execdir rename 's/.cpython-36././' {} \;