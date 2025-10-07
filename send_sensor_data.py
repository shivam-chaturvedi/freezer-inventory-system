#!/usr/bin/env python3
"""
Sensor Data Sender for Dashboard Integration
Continuously reads CO2 sensor and sends data to Flask app
"""

import serial
import time
import requests
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SensorDataSender:
    def __init__(self, flask_url="http://localhost:5000"):
        self.flask_url = flask_url
        self.co2_serial = None
        self.setup_co2_sensor()
        
    def setup_co2_sensor(self):
        """Setup MH-Z19E CO2 sensor"""
        try:
            self.co2_serial = serial.Serial(
                port='/dev/serial0',
                baudrate=9600,
                timeout=3,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            logger.info("✓ CO2 sensor connected")
            time.sleep(2)  # Let sensor stabilize
        except Exception as e:
            logger.error(f"✗ CO2 sensor error: {e}")
            self.co2_serial = None
    
    def calculate_checksum(self, data):
        """Calculate checksum for MH-Z19E sensor"""
        checksum = 0
        for i in range(1, 8):
            checksum += data[i]
        checksum = (~checksum) & 0xFF
        checksum += 1
        return checksum & 0xFF
    
    def read_co2(self):
        """Read CO2 concentration"""
        if not self.co2_serial:
            return None
            
        try:
            self.co2_serial.flushInput()
            self.co2_serial.flushOutput()
            
            # Send read command
            command = b'\xff\x01\x86\x00\x00\x00\x00\x00\x79'
            self.co2_serial.write(command)
            time.sleep(0.2)
            
            # Read response
            response = self.co2_serial.read(9)
            
            if len(response) == 9 and response[0] == 0xff and response[1] == 0x86:
                co2_high = response[2]
                co2_low = response[3]
                co2_concentration = (co2_high * 256) + co2_low
                return co2_concentration
                
        except Exception as e:
            logger.error(f"Error reading CO2: {e}")
            
        return None
    
    def assess_air_quality(self, co2_ppm):
        """Assess air quality based on CO2 level"""
        if co2_ppm is None:
            return 'unknown'
        elif co2_ppm < 400:
            return 'excellent'
        elif co2_ppm < 600:
            return 'good'
        elif co2_ppm < 800:
            return 'fair'
        elif co2_ppm < 1000:
            return 'moderate'
        elif co2_ppm < 1500:
            return 'poor'
        else:
            return 'very_poor'
    
    def send_sensor_data(self, co2_ppm):
        """Send sensor data to Flask app"""
        try:
            # Prepare sensor data
            sensor_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'co2_ppm': co2_ppm,
                'ammonia_ppm': None,  # Not available yet
                'h2s_ppm': None,      # Not available yet
                'door_open': False,   # Not available yet
                'air_quality': self.assess_air_quality(co2_ppm)
            }
            
            # Send to Flask app
            response = requests.post(
                f"{self.flask_url}/api/sensors",
                json=sensor_data,
                timeout=5
            )
            
            if response.status_code == 201:
                logger.info(f"✓ Sensor data sent: CO2={co2_ppm} PPM, Quality={sensor_data['air_quality']}")
                return True
            else:
                logger.error(f"✗ Failed to send sensor data: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error sending sensor data: {e}")
            return False
    
    def run_continuous_monitoring(self, interval=30):
        """Run continuous sensor monitoring"""
        logger.info(f"🚀 Starting continuous sensor monitoring (interval: {interval}s)")
        logger.info(f"📡 Sending data to: {self.flask_url}")
        
        reading_count = 0
        successful_sends = 0
        
        try:
            while True:
                reading_count += 1
                logger.info(f"\n--- Reading #{reading_count} ---")
                
                # Read CO2 sensor
                co2_value = self.read_co2()
                
                if co2_value is not None:
                    logger.info(f"CO2 Reading: {co2_value} PPM")
                    
                    # Send to dashboard
                    if self.send_sensor_data(co2_value):
                        successful_sends += 1
                    
                    # Calculate success rate
                    success_rate = (successful_sends / reading_count) * 100
                    logger.info(f"Success rate: {success_rate:.1f}% ({successful_sends}/{reading_count})")
                else:
                    logger.warning("Failed to read CO2 sensor")
                
                # Wait for next reading
                logger.info(f"Waiting {interval} seconds for next reading...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Error in monitoring: {e}")
        finally:
            self.cleanup()
    
    def run_single_reading(self):
        """Run single sensor reading and send to dashboard"""
        logger.info("🔬 Taking single sensor reading...")
        
        co2_value = self.read_co2()
        
        if co2_value is not None:
            logger.info(f"CO2 Reading: {co2_value} PPM")
            
            if self.send_sensor_data(co2_value):
                logger.info("✓ Data sent to dashboard successfully")
            else:
                logger.error("✗ Failed to send data to dashboard")
        else:
            logger.error("✗ Failed to read CO2 sensor")
        
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.co2_serial:
                self.co2_serial.close()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sensor Data Sender for Dashboard')
    parser.add_argument('--url', default='http://localhost:5000',
                       help='Flask application URL')
    parser.add_argument('--interval', type=int, default=30,
                       help='Sensor reading interval in seconds')
    parser.add_argument('--once', action='store_true',
                       help='Send single reading and exit')
    
    args = parser.parse_args()
    
    # Create sensor sender
    sender = SensorDataSender(flask_url=args.url)
    
    try:
        if args.once:
            sender.run_single_reading()
        else:
            sender.run_continuous_monitoring(interval=args.interval)
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        sender.cleanup()

if __name__ == "__main__":
    main()
