#!/bin/bash
# Fixed auto-start script for Pi Display
# This script starts the freezer system and opens the display

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

echo "Starting Freezer Pi Display System..."

# Check if virtual environment exists
if [ ! -d "freezer_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv freezer_env
fi

# Activate virtual environment
echo "Activating virtual environment..."
source freezer_env/bin/activate

# Install requirements if needed
echo "Installing/updating requirements..."
pip install -r requirements-simple.txt

# Fix database schema
echo "Fixing database schema..."
python3 fix_database.py

# Start the freezer system in background
echo "Starting Flask application..."
python3 app.py &
FLASK_PID=$!

# Wait for Flask to start
echo "Waiting for Flask to start..."
sleep 5

# Check if Flask is running
if ps -p $FLASK_PID > /dev/null; then
    echo "Flask started successfully (PID: $FLASK_PID)"
    
    # Get the Pi's IP address
    PI_IP=$(hostname -I | awk '{print $1}')
    
    # Open the Pi display
    echo "Opening Pi display..."
    echo "Display URL: http://$PI_IP:5000/pi"
    echo "Local URL: http://localhost:5000/pi"
    
    # Try different methods to open browser
    if command -v chromium &> /dev/null; then
        echo "Opening with Chromium..."
        chromium --kiosk --disable-infobars --disable-session-crashed-bubble --disable-web-security --user-data-dir=/tmp/chrome_temp --no-first-run --no-default-browser-check "http://localhost:5000/pi" &
    elif command -v firefox &> /dev/null; then
        echo "Opening with Firefox..."
        firefox --kiosk "http://localhost:5000/pi" &
    elif command -v midori &> /dev/null; then
        echo "Opening with Midori..."
        midori -e Fullscreen -a "http://localhost:5000/pi" &
    else
        echo "No suitable browser found."
        echo "Please open http://localhost:5000/pi manually in your browser"
        echo "Or install a browser:"
        echo "  sudo apt install chromium-browser"
        echo "  sudo apt install firefox"
        echo "  sudo apt install midori"
    fi
    
    echo ""
    echo "Pi Display System started successfully!"
    echo "Display is available at: http://$PI_IP:5000/pi"
    echo "Press Ctrl+C to stop the system"
    echo ""
    
    # Keep the script running
    wait $FLASK_PID
else
    echo "Failed to start Flask application"
    exit 1
fi
