#!/bin/bash
# Start Freezer Dashboard with Sensor Monitoring

echo "🌡️ Starting Freezer Dashboard with Sensor Monitoring..."

# Activate virtual environment
echo "📦 Activating virtual environment..."
source freezer_env/bin/activate

# Install/update requirements
echo "📋 Installing requirements..."
pip install -r requirements-simple.txt

# Start the dashboard with sensors
echo "🚀 Starting dashboard with sensor monitoring..."
python3 start_dashboard_with_sensors.py
