#!/bin/bash
# Final auto-start script for Pi Display
# This script handles port conflicts and starts the display

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

# Kill any existing Flask processes
echo "Stopping any existing Flask processes..."
pkill -f "python.*app.py" || true
sleep 2

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
    
    # Open with Chromium in fullscreen
    echo "Opening with Chromium in fullscreen mode..."
    chromium --kiosk --disable-infobars --disable-session-crashed-bubble --disable-web-security --user-data-dir=/tmp/chrome_temp --no-first-run --no-default-browser-check "http://localhost:5000/pi" &
    
    echo ""
    echo "🎉 Pi Display System started successfully!"
    echo "📱 Display is available at: http://$PI_IP:5000/pi"
    echo "🖥️  Professional interface is now running on your 5-inch display"
    echo ""
    echo "Press Ctrl+C to stop the system"
    echo ""
    
    # Keep the script running
    wait $FLASK_PID
else
    echo "❌ Failed to start Flask application"
    echo "Trying to start on a different port..."
    
    # Try port 5001
    PORT=5001 python3 app.py &
    FLASK_PID=$!
    sleep 3
    
    if ps -p $FLASK_PID > /dev/null; then
        echo "✅ Flask started on port 5001"
        echo "Display URL: http://$PI_IP:5001/pi"
        chromium --kiosk --disable-infobars --disable-session-crashed-bubble --disable-web-security --user-data-dir=/tmp/chrome_temp --no-first-run --no-default-browser-check "http://localhost:5001/pi" &
        wait $FLASK_PID
    else
        echo "❌ Failed to start Flask on any port"
        exit 1
    fi
fi
