#!/usr/bin/env python3
"""
Comprehensive Sensor Testing Script for Raspberry Pi 3
Tests MQ137 (Ammonia), MQ136 (H2S), and MH-Z19E (CO2) sensors
"""

import time
import json
import serial
import logging
from datetime import datetime

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

class SensorTester:
    def __init__(self):
        self.co2_serial = None
        self.ads = None
        self.mq137_channel = None
        self.mq136_channel = None
        
        # Initialize sensors
        self.setup_co2_sensor()
        self.setup_adc()
        
    def setup_co2_sensor(self):
        """Setup MH-Z19E CO2 sensor"""
        print("Setting up MH-Z19E CO2 sensor...")
        
        # Try different serial ports
        possible_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyAMA0', '/dev/serial0']
        
        for port in possible_ports:
            try:
                self.co2_serial = serial.Serial(
                    port=port,
                    baudrate=9600,
                    timeout=2
                )
                print(f"✓ CO2 sensor connected on {port}")
                time.sleep(2)  # Wait for sensor to stabilize
                return
            except Exception as e:
                print(f"✗ Failed to connect to {port}: {e}")
                continue
        
        print("✗ CO2 sensor not found on any port")
        self.co2_serial = None
    
    def setup_adc(self):
        """Setup ADS1115 ADC for MQ sensors"""
        if not ADC_AVAILABLE:
            print("✗ ADC modules not available")
            return
            
        print("Setting up ADS1115 ADC...")
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS.ADS1115(self.i2c)
            
            # MQ sensor channels
            self.mq137_channel = AnalogIn(self.ads, ADS.P0)  # Ammonia
            self.mq136_channel = AnalogIn(self.ads, ADS.P1)  # H2S
            
            print("✓ ADS1115 ADC connected")
            print(f"  - MQ137 (Ammonia) on Channel 0")
            print(f"  - MQ136 (H2S) on Channel 1")
            
        except Exception as e:
            print(f"✗ ADC setup failed: {e}")
            self.ads = None
            self.mq137_channel = None
            self.mq136_channel = None
    
    def test_co2_sensor(self):
        """Test MH-Z19E CO2 sensor"""
        print("\n" + "="*50)
        print("Testing MH-Z19E CO2 Sensor")
        print("="*50)
        
        if not self.co2_serial:
            print("✗ CO2 sensor not available")
            return None
        
        try:
            # Send read command
            self.co2_serial.write(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79')
            time.sleep(0.1)
            
            # Read response
            response = self.co2_serial.read(9)
            
            if len(response) == 9:
                # Check checksum
                checksum = sum(response[1:8]) & 0xFF
                if checksum == response[8]:
                    co2_high = response[2]
                    co2_low = response[3]
                    co2_concentration = (co2_high * 256) + co2_low
                    
                    print(f"✓ CO2 Reading: {co2_concentration} PPM")
                    print(f"  Raw response: {[hex(x) for x in response]}")
                    print(f"  Checksum: {checksum:02x} (expected: {response[8]:02x})")
                    
                    return co2_concentration
                else:
                    print(f"✗ Checksum error: {checksum:02x} != {response[8]:02x}")
            else:
                print(f"✗ Invalid response length: {len(response)} bytes")
                print(f"  Raw response: {[hex(x) for x in response]}")
            
        except Exception as e:
            print(f"✗ Error reading CO2 sensor: {e}")
        
        return None
    
    def test_mq137_ammonia(self):
        """Test MQ137 Ammonia sensor"""
        print("\n" + "="*50)
        print("Testing MQ137 Ammonia Sensor")
        print("="*50)
        
        if not self.mq137_channel:
            print("✗ MQ137 sensor not available")
            return None
        
        try:
            # Take multiple readings for stability
            readings = []
            for i in range(5):
                raw_value = self.mq137_channel.value
                voltage = self.mq137_channel.voltage
                readings.append((raw_value, voltage))
                time.sleep(0.5)
            
            # Calculate average
            avg_raw = sum(r[0] for r in readings) / len(readings)
            avg_voltage = sum(r[1] for r in readings) / len(readings)
            
            # Convert to PPM (simplified conversion)
            ammonia_ppm = max(0, (avg_voltage - 0.1) * 1000) if avg_voltage > 0.1 else 0
            
            print(f"✓ MQ137 Readings:")
            print(f"  Raw ADC: {avg_raw:.0f}")
            print(f"  Voltage: {avg_voltage:.3f}V")
            print(f"  Ammonia: {ammonia_ppm:.2f} PPM")
            print(f"  All readings: {[(r[0], f'{r[1]:.3f}V') for r in readings]}")
            
            return {
                'raw_value': avg_raw,
                'voltage': avg_voltage,
                'ammonia_ppm': ammonia_ppm
            }
            
        except Exception as e:
            print(f"✗ Error reading MQ137 sensor: {e}")
            return None
    
    def test_mq136_h2s(self):
        """Test MQ136 H2S sensor"""
        print("\n" + "="*50)
        print("Testing MQ136 H2S Sensor")
        print("="*50)
        
        if not self.mq136_channel:
            print("✗ MQ136 sensor not available")
            return None
        
        try:
            # Take multiple readings for stability
            readings = []
            for i in range(5):
                raw_value = self.mq136_channel.value
                voltage = self.mq136_channel.voltage
                readings.append((raw_value, voltage))
                time.sleep(0.5)
            
            # Calculate average
            avg_raw = sum(r[0] for r in readings) / len(readings)
            avg_voltage = sum(r[1] for r in readings) / len(readings)
            
            # Convert to PPM (simplified conversion)
            h2s_ppm = max(0, (avg_voltage - 0.1) * 2000) if avg_voltage > 0.1 else 0
            
            print(f"✓ MQ136 Readings:")
            print(f"  Raw ADC: {avg_raw:.0f}")
            print(f"  Voltage: {avg_voltage:.3f}V")
            print(f"  H2S: {h2s_ppm:.2f} PPM")
            print(f"  All readings: {[(r[0], f'{r[1]:.3f}V') for r in readings]}")
            
            return {
                'raw_value': avg_raw,
                'voltage': avg_voltage,
                'h2s_ppm': h2s_ppm
            }
            
        except Exception as e:
            print(f"✗ Error reading MQ136 sensor: {e}")
            return None
    
    def test_all_sensors(self):
        """Test all sensors"""
        print("\n" + "="*60)
        print("COMPREHENSIVE SENSOR TEST")
        print("="*60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'co2_ppm': None,
            'ammonia_data': None,
            'h2s_data': None,
            'test_status': 'running'
        }
        
        # Test CO2 sensor
        co2_value = self.test_co2_sensor()
        results['co2_ppm'] = co2_value
        
        # Test MQ137 Ammonia sensor
        ammonia_data = self.test_mq137_ammonia()
        results['ammonia_data'] = ammonia_data
        
        # Test MQ136 H2S sensor
        h2s_data = self.test_mq136_h2s()
        results['h2s_data'] = h2s_data
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        if co2_value is not None:
            print(f"✓ CO2: {co2_value} PPM")
        else:
            print("✗ CO2: Failed")
        
        if ammonia_data:
            print(f"✓ Ammonia: {ammonia_data['ammonia_ppm']:.2f} PPM ({ammonia_data['voltage']:.3f}V)")
        else:
            print("✗ Ammonia: Failed")
        
        if h2s_data:
            print(f"✓ H2S: {h2s_data['h2s_ppm']:.2f} PPM ({h2s_data['voltage']:.3f}V)")
        else:
            print("✗ H2S: Failed")
        
        results['test_status'] = 'completed'
        return results
    
    def continuous_test(self, duration=60, interval=5):
        """Run continuous testing for specified duration"""
        print(f"\nStarting continuous test for {duration} seconds (interval: {interval}s)")
        print("Press Ctrl+C to stop early")
        
        start_time = time.time()
        test_count = 0
        
        try:
            while time.time() - start_time < duration:
                test_count += 1
                print(f"\n--- Test Run #{test_count} ---")
                
                results = self.test_all_sensors()
                
                # Save results to file
                with open(f'sensor_test_{test_count}.json', 'w') as f:
                    json.dump(results, f, indent=2)
                
                if test_count < duration // interval:
                    print(f"Waiting {interval} seconds for next test...")
                    time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nTest stopped by user")
        
        print(f"\nCompleted {test_count} test runs")
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.co2_serial:
                self.co2_serial.close()
            if GPIO_AVAILABLE:
                GPIO.cleanup()
            print("Cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sensor Testing Tool')
    parser.add_argument('--continuous', type=int, metavar='SECONDS',
                       help='Run continuous testing for specified duration')
    parser.add_argument('--interval', type=int, default=5,
                       help='Interval between tests in continuous mode')
    parser.add_argument('--co2-only', action='store_true',
                       help='Test only CO2 sensor')
    parser.add_argument('--mq-only', action='store_true',
                       help='Test only MQ sensors')
    
    args = parser.parse_args()
    
    # Create tester
    tester = SensorTester()
    
    try:
        if args.continuous:
            tester.continuous_test(duration=args.continuous, interval=args.interval)
        elif args.co2_only:
            tester.test_co2_sensor()
        elif args.mq_only:
            tester.test_mq137_ammonia()
            tester.test_mq136_h2s()
        else:
            tester.test_all_sensors()
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
