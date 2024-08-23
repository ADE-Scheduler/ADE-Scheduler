#!/bin/bash
# Go to folder

cd /ADE-Scheduler

# venv environment
source /ADE-Scheduler/venv/bin/activate

# Run poetry to install modules from pyproject.toml
source ~/.bashrc
poetry install

# Create .flaskenv from default
if [ ! -f ".flaskenv" ]; then
    echo "Creating .flaskenv..."
    cp .flaskenv.default .flaskenv
fi

#  Run Redis
redis-server &


# Run postgresql
# this is complicated, use sqlite for dev instead lol
flask sql init

# Run Flask !
echo "Running Flask..."
flask run
