#!/bin/bash
# Auto-start script for Pi Display on 5-inch LCD
# This script ensures the dashboard opens automatically on startup

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

echo "=== Starting Freezer Pi Display System ==="
echo "Timestamp: $(date)"
echo "Working directory: $SCRIPT_DIR"

# Wait for network to be available
echo "Waiting for network connection..."
while ! ping -c 1 google.com &> /dev/null; do
    echo "Waiting for network..."
    sleep 2
done
echo "Network connection established"

# Wait for display to be ready
echo "Waiting for display to be ready..."
sleep 5

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
pkill -f "chromium" || true
sleep 3

# Configure display for 5-inch LCD
echo "Configuring display for 5-inch LCD..."
export DISPLAY=:0

# Set display resolution and rotation if needed
# Uncomment and modify these lines based on your 5-inch display specs
# xrandr --output HDMI-1 --mode 800x480 --rotate normal
# xrandr --output HDMI-1 --mode 1024x600 --rotate normal

# Start the Flask application
echo "Starting Flask application..."
python3 app.py &
FLASK_PID=$!

# Wait for Flask to start
echo "Waiting for Flask to start..."
sleep 8

# Check if Flask is running
if ps -p $FLASK_PID > /dev/null; then
    echo "✅ Flask started successfully (PID: $FLASK_PID)"
    
    # Get the Pi's IP address
    PI_IP=$(hostname -I | awk '{print $1}')
    
    # Display URLs
    echo "📱 Display URLs:"
    echo "   Local: http://localhost:5000/pi"
    echo "   Network: http://$PI_IP:5000/pi"
    
    # Wait a bit more for Flask to fully initialize
    sleep 3
    
    # Open with Chromium in fullscreen kiosk mode
    echo "Opening Chromium in fullscreen kiosk mode..."
    chromium-browser \
        --kiosk \
        --disable-infobars \
        --disable-session-crashed-bubble \
        --disable-web-security \
        --disable-features=TranslateUI \
        --disable-ipc-flooding-protection \
        --user-data-dir=/tmp/chrome_temp_$(date +%s) \
        --no-first-run \
        --no-default-browser-check \
        --disable-background-timer-throttling \
        --disable-backgrounding-occluded-windows \
        --disable-renderer-backgrounding \
        --disable-field-trial-config \
        --disable-back-forward-cache \
        --disable-ipc-flooding-protection \
        --autoplay-policy=no-user-gesture-required \
        --disable-extensions \
        --disable-plugins \
        --disable-default-apps \
        --no-sandbox \
        "http://localhost:5000/pi" &
    
    CHROMIUM_PID=$!
    
    echo ""
    echo "🎉 Pi Display System started successfully!"
    echo "🖥️  Dashboard is now running on your 5-inch LCD display"
    echo "📱 You can also access it from other devices at: http://$PI_IP:5000/pi"
    echo ""
    echo "Process IDs:"
    echo "   Flask: $FLASK_PID"
    echo "   Chromium: $CHROMIUM_PID"
    echo ""
    echo "Press Ctrl+C to stop the system"
    echo ""
    
    # Function to cleanup on exit
    cleanup() {
        echo ""
        echo "Shutting down display system..."
        kill $FLASK_PID 2>/dev/null || true
        kill $CHROMIUM_PID 2>/dev/null || true
        pkill -f "python.*app.py" || true
        pkill -f "chromium" || true
        echo "System stopped"
        exit 0
    }
    
    # Set up signal handlers
    trap cleanup SIGINT SIGTERM
    
    # Keep the script running and monitor processes
    while true; do
        if ! ps -p $FLASK_PID > /dev/null; then
            echo "❌ Flask process died, restarting..."
            python3 app.py &
            FLASK_PID=$!
            sleep 5
        fi
        
        if ! ps -p $CHROMIUM_PID > /dev/null; then
            echo "❌ Chromium process died, restarting..."
            chromium-browser \
                --kiosk \
                --disable-infobars \
                --disable-session-crashed-bubble \
                --disable-web-security \
                --user-data-dir=/tmp/chrome_temp_$(date +%s) \
                --no-first-run \
                --no-default-browser-check \
                "http://localhost:5000/pi" &
            CHROMIUM_PID=$!
        fi
        
        sleep 10
    done
    
else
    echo "❌ Failed to start Flask application"
    echo "Trying alternative startup methods..."
    
    # Try starting with different port
    echo "Trying port 5001..."
    PORT=5001 python3 app.py &
    FLASK_PID=$!
    sleep 5
    
    if ps -p $FLASK_PID > /dev/null; then
        echo "✅ Flask started on port 5001"
        echo "Display URL: http://$PI_IP:5001/pi"
        chromium-browser --kiosk --disable-infobars --disable-session-crashed-bubble --disable-web-security --user-data-dir=/tmp/chrome_temp --no-first-run --no-default-browser-check "http://localhost:5001/pi" &
        wait $FLASK_PID
    else
        echo "❌ Failed to start Flask on any port"
        echo "Please check the error messages above"
        exit 1
    fi
fi
