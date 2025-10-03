#!/usr/bin/env python3
"""
Raspberry Pi Sensor Integration for Freezer Inventory System
This script reads sensor data and sends it to the Flask application
"""

import RPi.GPIO as GPIO
import Adafruit_DHT
import requests
import time
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FreezerSensors:
    def __init__(self, flask_url="http://localhost:5000"):
        self.flask_url = flask_url
        
        # Sensor configuration
        self.dht_sensor = Adafruit_DHT.DHT22
        self.dht_pin = 4  # GPIO pin for DHT22 sensor
        
        # Door sensor configuration
        self.door_sensor_pin = 18  # GPIO pin for door sensor (magnetic switch)
        
        # Light sensor configuration (optional)
        self.light_sensor_pin = 24  # GPIO pin for light sensor (LDR)
        
        # Setup GPIO
        self.setup_gpio()
        
    def setup_gpio(self):
        """Initialize GPIO pins"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.door_sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.light_sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            logger.info("GPIO setup completed")
        except Exception as e:
            logger.error(f"Error setting up GPIO: {e}")
    
    def read_temperature_humidity(self):
        """Read temperature and humidity from DHT22 sensor"""
        try:
            humidity, temperature = Adafruit_DHT.read_retry(self.dht_sensor, self.dht_pin)
            if humidity is not None and temperature is not None:
                return {
                    'temperature': round(temperature, 2),
                    'humidity': round(humidity, 2)
                }
            else:
                logger.warning("Failed to read DHT22 sensor")
                return None
        except Exception as e:
            logger.error(f"Error reading DHT22 sensor: {e}")
            return None
    
    def read_door_status(self):
        """Read door status from magnetic switch"""
        try:
            # Magnetic switch: LOW when door is closed, HIGH when door is open
            door_open = GPIO.input(self.door_sensor_pin)
            return bool(door_open)
        except Exception as e:
            logger.error(f"Error reading door sensor: {e}")
            return None
    
    def read_light_level(self):
        """Read light level from LDR sensor (optional)"""
        try:
            # This is a simple implementation - you might need to adjust based on your LDR setup
            light_level = GPIO.input(self.light_sensor_pin)
            return light_level
        except Exception as e:
            logger.error(f"Error reading light sensor: {e}")
            return None
    
    def read_all_sensors(self):
        """Read all sensor data"""
        sensor_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'temperature': None,
            'humidity': None,
            'door_open': None,
            'light_level': None
        }
        
        # Read temperature and humidity
        temp_humidity = self.read_temperature_humidity()
        if temp_humidity:
            sensor_data.update(temp_humidity)
        
        # Read door status
        door_status = self.read_door_status()
        if door_status is not None:
            sensor_data['door_open'] = door_status
        
        # Read light level
        light_level = self.read_light_level()
        if light_level is not None:
            sensor_data['light_level'] = light_level
        
        return sensor_data
    
    def send_sensor_data(self, sensor_data):
        """Send sensor data to Flask application"""
        try:
            response = requests.post(
                f"{self.flask_url}/api/sensors",
                json=sensor_data,
                timeout=5
            )
            if response.status_code == 201:
                logger.info("Sensor data sent successfully")
                return True
            else:
                logger.error(f"Failed to send sensor data: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending sensor data: {e}")
            return False
    
    def check_spoilage_conditions(self, sensor_data):
        """Check for conditions that might cause spoilage"""
        warnings = []
        
        # Temperature check
        if sensor_data.get('temperature') and sensor_data['temperature'] > 4:
            warnings.append(f"Temperature too high: {sensor_data['temperature']}°C")
        
        # Humidity check
        if sensor_data.get('humidity') and sensor_data['humidity'] > 80:
            warnings.append(f"Humidity too high: {sensor_data['humidity']}%")
        
        # Door open check
        if sensor_data.get('door_open'):
            warnings.append("Door is open")
        
        return warnings
    
    def run_continuous_monitoring(self, interval=30):
        """Run continuous sensor monitoring"""
        logger.info(f"Starting continuous monitoring (interval: {interval}s)")
        
        try:
            while True:
                # Read all sensors
                sensor_data = self.read_all_sensors()
                logger.info(f"Sensor data: {sensor_data}")
                
                # Send data to Flask app
                self.send_sensor_data(sensor_data)
                
                # Check for spoilage conditions
                warnings = self.check_spoilage_conditions(sensor_data)
                if warnings:
                    logger.warning(f"Spoilage warnings: {', '.join(warnings)}")
                
                # Wait for next reading
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error in continuous monitoring: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up GPIO resources"""
        try:
            GPIO.cleanup()
            logger.info("GPIO cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Freezer Sensor Monitor')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Flask application URL')
    parser.add_argument('--interval', type=int, default=30, 
                       help='Sensor reading interval in seconds')
    parser.add_argument('--once', action='store_true', 
                       help='Read sensors once and exit')
    
    args = parser.parse_args()
    
    # Create sensor monitor
    monitor = FreezerSensors(flask_url=args.url)
    
    if args.once:
        # Single reading
        sensor_data = monitor.read_all_sensors()
        print(json.dumps(sensor_data, indent=2))
        monitor.send_sensor_data(sensor_data)
    else:
        # Continuous monitoring
        monitor.run_continuous_monitoring(interval=args.interval)

if __name__ == "__main__":
    main()

