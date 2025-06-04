#!/bin/bash

# Startup script for the OAuthentic backend server

echo "Starting OAuthentic Backend Server..."

# Navigate to the project directory
cd "$(dirname "$0")" || exit

# Checking out the virtual environment
source .oauthvenv/bin/activate
# Check if the virtual environment is activated
if [ "$VIRTUAL_ENV" != "" ]; then
    echo "Virtual environment activated: $VIRTUAL_ENV"
else
    echo "Failed to activate virtual environment."
    exit 1
fi

# Export environment variables if needed
export APP_ENV=development
export PORT=8080


# Install dependencies
# echo "Installing dependencies..."
# pip3 install

# Initialize the database
echo "Initializing the database..."
python3 init_db.py # For now this will change to migration later
# Start the server
echo "Starting the server on port $PORT..."
# npm start
python3 server.py