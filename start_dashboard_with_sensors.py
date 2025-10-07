#!/usr/bin/env python3
"""
Start Dashboard with Sensor Monitoring
Runs Flask app and sensor monitoring together
"""

import subprocess
import time
import signal
import sys
import os
from threading import Thread

class DashboardWithSensors:
    def __init__(self):
        self.flask_process = None
        self.sensor_process = None
        self.running = True
        
    def start_flask_app(self):
        """Start Flask application"""
        print("🚀 Starting Flask application...")
        try:
            self.flask_process = subprocess.Popen([
                'python3', 'app.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✓ Flask app started on http://localhost:5000")
            return True
        except Exception as e:
            print(f"✗ Failed to start Flask app: {e}")
            return False
    
    def start_sensor_monitoring(self):
        """Start sensor monitoring"""
        print("🌡️ Starting sensor monitoring...")
        try:
            self.sensor_process = subprocess.Popen([
                'python3', 'send_sensor_data.py', '--interval', '30'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✓ Sensor monitoring started")
            return True
        except Exception as e:
            print(f"✗ Failed to start sensor monitoring: {e}")
            return False
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up processes"""
        print("🧹 Cleaning up processes...")
        
        if self.sensor_process:
            try:
                self.sensor_process.terminate()
                self.sensor_process.wait(timeout=5)
                print("✓ Sensor monitoring stopped")
            except:
                self.sensor_process.kill()
                print("⚠ Sensor monitoring force stopped")
        
        if self.flask_process:
            try:
                self.flask_process.terminate()
                self.flask_process.wait(timeout=5)
                print("✓ Flask app stopped")
            except:
                self.flask_process.kill()
                print("⚠ Flask app force stopped")
    
    def run(self):
        """Run dashboard with sensors"""
        print("=" * 60)
        print("🌡️ FREEZER DASHBOARD WITH SENSOR MONITORING")
        print("=" * 60)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Start Flask app
        if not self.start_flask_app():
            print("❌ Failed to start Flask app. Exiting.")
            return
        
        # Wait a moment for Flask to start
        time.sleep(3)
        
        # Start sensor monitoring
        if not self.start_sensor_monitoring():
            print("⚠ Sensor monitoring failed, but Flask app is running")
        
        print("\n" + "=" * 60)
        print("✅ SYSTEM READY")
        print("=" * 60)
        print("🌐 Dashboard: http://localhost:5000")
        print("🌐 Touch Interface: http://localhost:5000/touch")
        print("🌐 Pi Display: http://localhost:5000/pi")
        print("=" * 60)
        print("Press Ctrl+C to stop all services")
        print("=" * 60)
        
        try:
            # Keep running until interrupted
            while self.running:
                time.sleep(1)
                
                # Check if processes are still running
                if self.flask_process and self.flask_process.poll() is not None:
                    print("❌ Flask app stopped unexpectedly")
                    break
                
                if self.sensor_process and self.sensor_process.poll() is not None:
                    print("⚠ Sensor monitoring stopped, restarting...")
                    self.start_sensor_monitoring()
                
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

def main():
    """Main function"""
    dashboard = DashboardWithSensors()
    dashboard.run()

if __name__ == "__main__":
    main()
