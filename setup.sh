#bin/bash

# Install poetry
which poetry || pip3 install poetry

# Install project dependencies
poetry install