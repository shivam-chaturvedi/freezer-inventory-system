#!/bin/bash
# Stop any running Flask processes

echo "Stopping Flask processes..."

# Kill Flask processes
pkill -f "python.*app.py" || true

# Wait a moment
sleep 2

# Check if any Flask processes are still running
if pgrep -f "python.*app.py" > /dev/null; then
    echo "Force killing Flask processes..."
    pkill -9 -f "python.*app.py" || true
    sleep 1
fi

# Check if port 5000 is still in use
if lsof -i :5000 > /dev/null 2>&1; then
    echo "Port 5000 is still in use. Killing process..."
    lsof -ti :5000 | xargs kill -9 || true
fi

echo "Flask processes stopped."
echo "You can now run: ./start_pi_display_final.sh"
