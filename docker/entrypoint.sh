#!/bin/bash
# Go to folder
cd /ADE-Scheduler

# Update & install Node deps (& run Webpack)
npm install
echo "Running Webpack..."
npx webpack --progress --watch --no-stats &

# Update & install Python deps
if [ ! -d "venv" ]; then
    echo "Installing virtualenv..."
    python3.9 -m venv venv
fi
source venv/bin/activate
pip install -r dev-requirements.txt

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
