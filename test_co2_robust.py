#!/usr/bin/env python3
"""
Robust CO2 Sensor Testing Script
Handles checksum errors and timing issues with MH-Z19E
"""

import serial
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RobustCO2Tester:
    def __init__(self):
        self.co2_serial = None
        self.setup_co2_sensor()
    
    def setup_co2_sensor(self):
        """Setup MH-Z19E CO2 sensor with robust configuration"""
        print("Setting up MH-Z19E CO2 sensor...")
        
        try:
            self.co2_serial = serial.Serial(
                port='/dev/serial0',
                baudrate=9600,
                timeout=5,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            print("✓ CO2 sensor connected on /dev/serial0")
            
            # Wait for sensor to stabilize
            print("Waiting for sensor to stabilize...")
            time.sleep(5)
            
            # Clear any old data
            self.co2_serial.flushInput()
            self.co2_serial.flushOutput()
            
            print("✓ Sensor ready for testing")
            
        except Exception as e:
            print(f"✗ Failed to connect to CO2 sensor: {e}")
            self.co2_serial = None
    
    def read_co2_robust(self, max_retries=5):
        """Read CO2 with multiple retry attempts"""
        if not self.co2_serial:
            return None
        
        for attempt in range(max_retries):
            try:
                print(f"\n--- Attempt {attempt + 1}/{max_retries} ---")
                
                # Clear buffers
                self.co2_serial.flushInput()
                self.co2_serial.flushOutput()
                
                # Send read command
                command = b'\xff\x01\x86\x00\x00\x00\x00\x00\x79'
                print(f"Sending command: {[hex(x) for x in command]}")
                
                self.co2_serial.write(command)
                time.sleep(0.1)
                
                # Read response
                response = self.co2_serial.read(9)
                print(f"Raw response: {[hex(x) for x in response]} (length: {len(response)})")
                
                if len(response) == 9:
                    # Check if response starts with correct header
                    if response[0] == 0xff and response[1] == 0x86:
                        # Calculate checksum
                        checksum = sum(response[1:8]) & 0xFF
                        expected_checksum = response[8]
                        
                        print(f"Checksum: {checksum:02x} (expected: {expected_checksum:02x})")
                        
                        if checksum == expected_checksum:
                            # Parse CO2 concentration
                            co2_high = response[2]
                            co2_low = response[3]
                            co2_concentration = (co2_high * 256) + co2_low
                            
                            print(f"✓ CO2 Reading: {co2_concentration} PPM")
                            return co2_concentration
                        else:
                            print(f"✗ Checksum error: {checksum:02x} != {expected_checksum:02x}")
                    else:
                        print(f"✗ Invalid header: {response[0]:02x} {response[1]:02x}")
                else:
                    print(f"✗ Invalid response length: {len(response)} bytes")
                
                # Wait before retry
                if attempt < max_retries - 1:
                    print("Waiting before retry...")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"✗ Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
        
        print("✗ All attempts failed")
        return None
    
    def test_co2_continuous(self, duration=60, interval=5):
        """Test CO2 sensor continuously"""
        print(f"\nStarting continuous CO2 testing for {duration} seconds")
        print(f"Reading every {interval} seconds...")
        print("Press Ctrl+C to stop early\n")
        
        start_time = time.time()
        reading_count = 0
        successful_readings = 0
        
        try:
            while time.time() - start_time < duration:
                reading_count += 1
                print(f"\n--- Reading #{reading_count} ---")
                
                co2_value = self.read_co2_robust()
                
                if co2_value is not None:
                    successful_readings += 1
                    print(f"✓ Success! CO2: {co2_value} PPM")
                else:
                    print("✗ Failed to read CO2")
                
                # Wait for next reading
                if time.time() - start_time < duration:
                    print(f"Waiting {interval} seconds...")
                    time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nTest stopped by user")
        
        print(f"\n--- Test Summary ---")
        print(f"Total readings attempted: {reading_count}")
        print(f"Successful readings: {successful_readings}")
        print(f"Success rate: {(successful_readings/reading_count)*100:.1f}%")
    
    def test_co2_single(self):
        """Test CO2 sensor with single reading"""
        print("\n" + "="*50)
        print("Single CO2 Reading Test")
        print("="*50)
        
        co2_value = self.read_co2_robust()
        
        if co2_value is not None:
            print(f"\n✓ SUCCESS: CO2 = {co2_value} PPM")
            
            # Interpret the reading
            if co2_value < 400:
                print("Note: Very low CO2 - check sensor or environment")
            elif co2_value < 1000:
                print("Note: Good air quality")
            elif co2_value < 2000:
                print("Note: Moderate CO2 levels")
            else:
                print("Note: High CO2 levels - poor ventilation")
        else:
            print("\n✗ FAILED: Could not read CO2 sensor")
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.co2_serial:
                self.co2_serial.close()
            print("Cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Robust CO2 Sensor Tester')
    parser.add_argument('--continuous', type=int, metavar='SECONDS',
                       help='Run continuous testing for specified duration')
    parser.add_argument('--interval', type=int, default=5,
                       help='Interval between readings in continuous mode')
    
    args = parser.parse_args()
    
    # Create tester
    tester = RobustCO2Tester()
    
    try:
        if args.continuous:
            tester.test_co2_continuous(duration=args.continuous, interval=args.interval)
        else:
            tester.test_co2_single()
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
