#!/usr/bin/env python3
"""
Raspberry Pi Sensor Integration for Freezer Inventory System
This script reads sensor data from MH-Z19E (CO2), MQ137 (Ammonia), and MQ136 (H2S) sensors
"""

import requests
import time
import json
import serial
from datetime import datetime
import logging

# Try to import Raspberry Pi specific modules
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    print("Warning: RPi.GPIO not available - GPIO functions will be disabled")
    GPIO_AVAILABLE = False

try:
    import busio
    import board
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    ADC_AVAILABLE = True
except ImportError:
    print("Warning: ADC modules not available - MQ sensor readings will be disabled")
    ADC_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FreezerSensors:
    def __init__(self, flask_url="http://localhost:5000"):
        self.flask_url = flask_url
        
        # Sensor configuration
        self.co2_serial_port = '/dev/ttyUSB0'  # USB port for MH-Z19E
        self.co2_baudrate = 9600
        
        # ADC configuration for MQ sensors
        if ADC_AVAILABLE:
            try:
                self.i2c = busio.I2C(board.SCL, board.SDA)
                self.ads = ADS.ADS1115(self.i2c)
                
                # MQ sensor channels
                self.mq137_channel = AnalogIn(self.ads, ADS.P0)  # Ammonia sensor
                self.mq136_channel = AnalogIn(self.ads, ADS.P1)  # H2S sensor
            except Exception as e:
                logger.error(f"Error setting up ADC: {e}")
                self.ads = None
                self.mq137_channel = None
                self.mq136_channel = None
        else:
            self.ads = None
            self.mq137_channel = None
            self.mq136_channel = None
        
        # Door sensor configuration (magnetic switch)
        self.door_sensor_pin = 18  # GPIO pin for door sensor
        
        # Setup GPIO
        self.setup_gpio()
        
        # CO2 sensor initialization
        self.setup_co2_sensor()
        
    def setup_gpio(self):
        """Initialize GPIO pins"""
        if not GPIO_AVAILABLE:
            logger.warning("GPIO not available - door sensor will be disabled")
            return
            
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.door_sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            logger.info("GPIO setup completed")
        except Exception as e:
            logger.error(f"Error setting up GPIO: {e}")
    
    def setup_co2_sensor(self):
        """Initialize CO2 sensor serial connection"""
        try:
            self.co2_serial = serial.Serial(
                port=self.co2_serial_port,
                baudrate=self.co2_baudrate,
                timeout=1
            )
            logger.info("CO2 sensor serial connection established")
        except Exception as e:
            logger.error(f"Error setting up CO2 sensor: {e}")
            self.co2_serial = None
    
    def read_co2(self):
        """Read CO2 concentration from MH-Z19E sensor"""
        if not self.co2_serial:
            return None
            
        try:
            # Send read command to MH-Z19E
            self.co2_serial.write(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79')
            time.sleep(0.1)
            
            # Read response
            response = self.co2_serial.read(9)
            if len(response) == 9:
                # Parse CO2 concentration (bytes 2 and 3)
                co2_high = response[2]
                co2_low = response[3]
                co2_concentration = (co2_high * 256) + co2_low
                return co2_concentration
            else:
                logger.warning("Invalid response from CO2 sensor")
                return None
        except Exception as e:
            logger.error(f"Error reading CO2 sensor: {e}")
            return None
    
    def read_mq137_ammonia(self):
        """Read ammonia concentration from MQ137 sensor"""
        if not ADC_AVAILABLE or not self.mq137_channel:
            return None
            
        try:
            # Read raw ADC value
            raw_value = self.mq137_channel.value
            voltage = self.mq137_channel.voltage
            
            # Convert to ammonia concentration (PPM)
            # This is a simplified conversion - you may need to calibrate
            # based on your specific sensor and environment
            ammonia_ppm = self.convert_mq_to_ppm(raw_value, voltage, 'ammonia')
            
            return {
                'raw_value': raw_value,
                'voltage': voltage,
                'ammonia_ppm': ammonia_ppm
            }
        except Exception as e:
            logger.error(f"Error reading MQ137 sensor: {e}")
            return None
    
    def read_mq136_h2s(self):
        """Read hydrogen sulfide concentration from MQ136 sensor"""
        if not ADC_AVAILABLE or not self.mq136_channel:
            return None
            
        try:
            # Read raw ADC value
            raw_value = self.mq136_channel.value
            voltage = self.mq136_channel.voltage
            
            # Convert to H2S concentration (PPM)
            h2s_ppm = self.convert_mq_to_ppm(raw_value, voltage, 'h2s')
            
            return {
                'raw_value': raw_value,
                'voltage': voltage,
                'h2s_ppm': h2s_ppm
            }
        except Exception as e:
            logger.error(f"Error reading MQ136 sensor: {e}")
            return None
    
    def convert_mq_to_ppm(self, raw_value, voltage, sensor_type):
        """Convert MQ sensor readings to PPM values"""
        # These are approximate conversion formulas
        # You should calibrate these based on your specific sensors and environment
        
        if sensor_type == 'ammonia':
            # MQ137 ammonia sensor conversion
            # This is a simplified linear approximation
            if voltage < 0.1:
                return 0
            # Rough conversion: higher voltage = higher ammonia concentration
            ammonia_ppm = (voltage - 0.1) * 1000  # Adjust multiplier as needed
            return max(0, ammonia_ppm)
        
        elif sensor_type == 'h2s':
            # MQ136 H2S sensor conversion
            if voltage < 0.1:
                return 0
            # Rough conversion: higher voltage = higher H2S concentration
            h2s_ppm = (voltage - 0.1) * 2000  # Adjust multiplier as needed
            return max(0, h2s_ppm)
        
        return 0
    
    def read_door_status(self):
        """Read door status from magnetic switch"""
        if not GPIO_AVAILABLE:
            return None
            
        try:
            # Magnetic switch: LOW when door is closed, HIGH when door is open
            door_open = GPIO.input(self.door_sensor_pin)
            return bool(door_open)
        except Exception as e:
            logger.error(f"Error reading door sensor: {e}")
            return None
    
    def read_all_sensors(self):
        """Read all sensor data"""
        sensor_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'co2_ppm': None,
            'ammonia_ppm': None,
            'h2s_ppm': None,
            'door_open': None,
            'air_quality': 'unknown'
        }
        
        # Read CO2 sensor
        co2_value = self.read_co2()
        if co2_value is not None:
            sensor_data['co2_ppm'] = co2_value
        
        # Read ammonia sensor
        ammonia_data = self.read_mq137_ammonia()
        if ammonia_data:
            sensor_data['ammonia_ppm'] = ammonia_data['ammonia_ppm']
        
        # Read H2S sensor
        h2s_data = self.read_mq136_h2s()
        if h2s_data:
            sensor_data['h2s_ppm'] = h2s_data['h2s_ppm']
        
        # Read door status
        door_status = self.read_door_status()
        if door_status is not None:
            sensor_data['door_open'] = door_status
        
        # Determine air quality based on sensor readings
        sensor_data['air_quality'] = self.assess_air_quality(
            sensor_data['co2_ppm'],
            sensor_data['ammonia_ppm'],
            sensor_data['h2s_ppm']
        )
        
        return sensor_data
    
    def assess_air_quality(self, co2, ammonia, h2s):
        """Assess air quality based on sensor readings"""
        if co2 is None and ammonia is None and h2s is None:
            return 'unknown'
        
        # CO2 levels (PPM)
        if co2 and co2 > 1000:  # High CO2 indicates poor ventilation
            return 'poor'
        
        # Ammonia levels (PPM) - indicator of spoiled food
        if ammonia and ammonia > 25:  # Threshold for ammonia from spoiled food
            return 'poor'
        
        # H2S levels (PPM) - indicator of spoiled food
        if h2s and h2s > 10:  # Threshold for H2S from spoiled food
            return 'poor'
        
        # If all readings are within normal ranges
        if (co2 is None or co2 <= 1000) and (ammonia is None or ammonia <= 25) and (h2s is None or h2s <= 10):
            return 'good'
        
        return 'moderate'
    
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
        
        # CO2 check - high CO2 might indicate door left open
        if sensor_data.get('co2_ppm') and sensor_data['co2_ppm'] > 1000:
            warnings.append(f"High CO2 detected: {sensor_data['co2_ppm']} PPM - check ventilation")
        
        # Ammonia check - high ammonia indicates spoiled food
        if sensor_data.get('ammonia_ppm') and sensor_data['ammonia_ppm'] > 25:
            warnings.append(f"High ammonia detected: {sensor_data['ammonia_ppm']:.2f} PPM - possible spoiled food")
        
        # H2S check - high H2S indicates spoiled food
        if sensor_data.get('h2s_ppm') and sensor_data['h2s_ppm'] > 10:
            warnings.append(f"High H2S detected: {sensor_data['h2s_ppm']:.2f} PPM - possible spoiled food")
        
        # Door open check
        if sensor_data.get('door_open'):
            warnings.append("Door is open")
        
        # Air quality check
        if sensor_data.get('air_quality') == 'poor':
            warnings.append("Poor air quality detected - check for spoiled food")
        
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
        """Clean up resources"""
        try:
            if hasattr(self, 'co2_serial') and self.co2_serial:
                self.co2_serial.close()
            if GPIO_AVAILABLE:
                GPIO.cleanup()
            logger.info("Cleanup completed")
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