#bin/bash

which pip3 || sudo apt-get install python3-pip

# Install poetry
which poetry || pip3 install poetry

# Install project dependencies
# TODO: Poetry script is installed in strange paths sometimes, ensure it's added to $PATH.
poetry install