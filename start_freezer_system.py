#!/usr/bin/env python3
"""
Startup script for the Freezer Inventory System
This script starts both the Flask web server and sensor monitoring
"""

import subprocess
import time
import signal
import sys
import os
from threading import Thread

class FreezerSystem:
    def __init__(self):
        self.flask_process = None
        self.sensor_process = None
        self.running = False
    
    def start_flask_app(self):
        """Start the Flask web application"""
        try:
            print("Starting Flask web application...")
            self.flask_process = subprocess.Popen([
                sys.executable, 'app.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Flask app started on http://0.0.0.0:5000")
            return True
        except Exception as e:
            print(f"Error starting Flask app: {e}")
            return False
    
    def start_sensor_monitoring(self):
        """Start the sensor monitoring process"""
        try:
            print("Starting sensor monitoring...")
            self.sensor_process = subprocess.Popen([
                sys.executable, 'sensors.py', '--interval', '30'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Sensor monitoring started")
            return True
        except Exception as e:
            print(f"Error starting sensor monitoring: {e}")
            return False
    
    def stop_processes(self):
        """Stop all running processes"""
        print("Stopping processes...")
        
        if self.sensor_process:
            self.sensor_process.terminate()
            try:
                self.sensor_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.sensor_process.kill()
        
        if self.flask_process:
            self.flask_process.terminate()
            try:
                self.flask_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.flask_process.kill()
        
        print("All processes stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down...")
        self.running = False
        self.stop_processes()
        sys.exit(0)
    
    def run(self):
        """Run the complete system"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("=== Freezer Inventory System ===")
        print("Starting system components...")
        
        # Start Flask app
        if not self.start_flask_app():
            print("Failed to start Flask app, exiting...")
            return
        
        # Wait a moment for Flask to start
        time.sleep(3)
        
        # Start sensor monitoring
        if not self.start_sensor_monitoring():
            print("Failed to start sensor monitoring, but Flask app is running")
        
        self.running = True
        
        print("\n=== System Status ===")
        print("Web Dashboard: http://localhost:5000")
        print("Touch Interface: http://localhost:5000/touch")
        print("Press Ctrl+C to stop the system")
        print("=" * 40)
        
        try:
            # Monitor processes
            while self.running:
                # Check if Flask process is still running
                if self.flask_process and self.flask_process.poll() is not None:
                    print("Flask app stopped unexpectedly")
                    break
                
                # Check if sensor process is still running
                if self.sensor_process and self.sensor_process.poll() is not None:
                    print("Sensor monitoring stopped unexpectedly")
                    # Restart sensor monitoring
                    if self.running:
                        print("Restarting sensor monitoring...")
                        self.start_sensor_monitoring()
                
                time.sleep(5)
        
        except KeyboardInterrupt:
            print("\nShutdown requested by user")
        
        finally:
            self.stop_processes()

def main():
    """Main function"""
    # Check if running on Raspberry Pi
    if not os.path.exists('/proc/device-tree/model'):
        print("Warning: This script is designed for Raspberry Pi")
        print("Sensor functionality may not work on other systems")
    
    # Check if required packages are installed
    try:
        import RPi.GPIO
        import Adafruit_DHT
        import flask
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return
    
    # Start the system
    system = FreezerSystem()
    system.run()

if __name__ == "__main__":
    main()

