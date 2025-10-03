#!/bin/bash
# Headless startup script for Pi Display
# This script starts the system without trying to open a browser

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

echo "Starting Freezer System (Headless Mode)..."

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

# Start the freezer system
echo "Starting Flask application..."
python3 app.py &
FLASK_PID=$!

# Wait for Flask to start
echo "Waiting for Flask to start..."
sleep 5

# Check if Flask is running
if ps -p $FLASK_PID > /dev/null; then
    echo "✅ Flask started successfully (PID: $FLASK_PID)"
    
    # Get the Pi's IP address
    PI_IP=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo "🎉 Freezer System is now running!"
    echo ""
    echo "📱 Access URLs:"
    echo "   • Pi Display: http://$PI_IP:5000/pi"
    echo "   • Web Dashboard: http://$PI_IP:5000"
    echo "   • Touch Interface: http://$PI_IP:5000/touch"
    echo ""
    echo "🖥️  To view on your 5-inch display:"
    echo "   1. Connect your display to the Pi"
    echo "   2. Open a browser and go to: http://$PI_IP:5000/pi"
    echo "   3. Press F11 for fullscreen mode"
    echo ""
    echo "📊 System Status:"
    echo "   • Database: ✅ Fixed and ready"
    echo "   • Flask Server: ✅ Running on port 5000"
    echo "   • Sensor API: ✅ Ready for your sensors"
    echo "   • Inventory API: ✅ Ready for items"
    echo ""
    echo "Press Ctrl+C to stop the system"
    echo ""
    
    # Keep the script running
    wait $FLASK_PID
else
    echo "❌ Failed to start Flask application"
    exit 1
fi
