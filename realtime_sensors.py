#!/usr/bin/env python3
"""
Real-time Sensor Monitoring for Terminal
Shows live CO2 readings with visual indicators
"""

import serial
import time
import os
import sys
from datetime import datetime

class RealtimeSensorMonitor:
    def __init__(self):
        self.co2_serial = None
        self.setup_co2_sensor()
        self.running = True
        
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
            print("✓ CO2 sensor connected")
            time.sleep(2)  # Let sensor stabilize
        except Exception as e:
            print(f"✗ CO2 sensor error: {e}")
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
            pass
            
        return None
    
    def get_co2_status(self, co2_value):
        """Get CO2 status with emoji indicators"""
        if co2_value is None:
            return "❌ ERROR", "red"
        elif co2_value < 400:
            return "🟢 EXCELLENT", "green"
        elif co2_value < 600:
            return "🟢 GOOD", "green"
        elif co2_value < 800:
            return "🟡 FAIR", "yellow"
        elif co2_value < 1000:
            return "🟡 MODERATE", "yellow"
        elif co2_value < 1500:
            return "🟠 POOR", "red"
        else:
            return "🔴 VERY POOR", "red"
    
    def get_co2_emoji(self, co2_value):
        """Get CO2 level emoji"""
        if co2_value is None:
            return "❌"
        elif co2_value < 400:
            return "🟢"
        elif co2_value < 800:
            return "🟡"
        elif co2_value < 1200:
            return "🟠"
        else:
            return "🔴"
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        """Print header information"""
        print("=" * 80)
        print("🌡️  REAL-TIME FREEZER SENSOR MONITORING")
        print("=" * 80)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 80)
    
    def print_sensor_data(self, co2_value, reading_count, success_rate):
        """Print sensor data in a nice format"""
        status, color = self.get_co2_status(co2_value)
        emoji = self.get_co2_emoji(co2_value)
        
        print(f"\n🔬 SENSOR READINGS")
        print("-" * 40)
        
        if co2_value is not None:
            print(f"CO₂ Level: {emoji} {co2_value:4d} PPM")
            print(f"Status:    {status}")
            
            # Air quality interpretation
            if co2_value < 400:
                print("💨 Air Quality: Excellent - Fresh outdoor air")
            elif co2_value < 600:
                print("💨 Air Quality: Good - Well ventilated")
            elif co2_value < 800:
                print("💨 Air Quality: Fair - Normal indoor levels")
            elif co2_value < 1000:
                print("💨 Air Quality: Moderate - Some ventilation needed")
            elif co2_value < 1500:
                print("⚠️  Air Quality: Poor - Ventilation required")
            else:
                print("🚨 Air Quality: Very Poor - Immediate ventilation needed")
        else:
            print("CO₂ Level: ❌ SENSOR ERROR")
            print("Status:    ❌ NO DATA")
        
        print(f"\n📊 STATISTICS")
        print("-" * 40)
        print(f"Readings:  {reading_count}")
        print(f"Success:   {success_rate:.1f}%")
        print(f"Uptime:    {datetime.now().strftime('%H:%M:%S')}")
    
    def print_controls(self):
        """Print control information"""
        print(f"\n🎮 CONTROLS")
        print("-" * 40)
        print("Press Ctrl+C to stop monitoring")
        print("Press 'q' + Enter to quit")
        print("Press 'r' + Enter to reset statistics")
    
    def run_realtime_monitor(self, update_interval=2):
        """Run real-time monitoring"""
        reading_count = 0
        successful_readings = 0
        start_time = time.time()
        
        print("🚀 Starting real-time sensor monitoring...")
        print("Press Ctrl+C to stop")
        time.sleep(2)
        
        try:
            while self.running:
                # Clear screen and print header
                self.clear_screen()
                self.print_header()
                
                # Read CO2 sensor
                co2_value = self.read_co2()
                reading_count += 1
                
                if co2_value is not None:
                    successful_readings += 1
                
                # Calculate success rate
                success_rate = (successful_readings / reading_count) * 100 if reading_count > 0 else 0
                
                # Print sensor data
                self.print_sensor_data(co2_value, reading_count, success_rate)
                
                # Print controls
                self.print_controls()
                
                # Wait for next update
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            self.running = False
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.cleanup()
    
    def run_simple_monitor(self, update_interval=2):
        """Run simple monitoring without clearing screen"""
        reading_count = 0
        successful_readings = 0
        
        print("🚀 Starting simple sensor monitoring...")
        print("Press Ctrl+C to stop")
        print("-" * 60)
        
        try:
            while self.running:
                # Read CO2 sensor
                co2_value = self.read_co2()
                reading_count += 1
                
                if co2_value is not None:
                    successful_readings += 1
                    status, _ = self.get_co2_status(co2_value)
                    emoji = self.get_co2_emoji(co2_value)
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] CO₂: {emoji} {co2_value:4d} PPM - {status}")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] CO₂: ❌ SENSOR ERROR")
                
                # Wait for next update
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
            self.running = False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.co2_serial:
                self.co2_serial.close()
        except:
            pass

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time Sensor Monitor')
    parser.add_argument('--interval', type=int, default=2,
                       help='Update interval in seconds (default: 2)')
    parser.add_argument('--simple', action='store_true',
                       help='Use simple monitoring (no screen clearing)')
    
    args = parser.parse_args()
    
    # Create monitor
    monitor = RealtimeSensorMonitor()
    
    try:
        if args.simple:
            monitor.run_simple_monitor(update_interval=args.interval)
        else:
            monitor.run_realtime_monitor(update_interval=args.interval)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        monitor.cleanup()

if __name__ == "__main__":
    main()
