# Sensor Setup and Testing Guide

## Hardware Connections

### Raspberry Pi 3 Pinout Reference
```
    3.3V  (1) (2)  5V
   GPIO2  (3) (4)  5V
   GPIO3  (5) (6)  GND
   GPIO4  (7) (8)  GPIO14 (TXD)
     GND  (9) (10) GPIO15 (RXD)
  GPIO17 (11) (12) GPIO18
  GPIO27 (13) (14) GND
  GPIO22 (15) (16) GPIO23
    3.3V (17) (18) GPIO24
  GPIO10 (19) (20) GND
   GPIO9 (21) (22) GPIO25
  GPIO11 (23) (24) GPIO8
     GND (25) (26) GPIO7
```

### 1. MH-Z19E CO2 Sensor Connections
```
MH-Z19E Pin    →    Raspberry Pi 3 Pin    →    Description
VCC            →    Pin 2 (5V)            →    Power supply
GND            →    Pin 6 (GND)           →    Ground
TX             →    Pin 10 (GPIO 15/RXD)  →    Serial data out
RX             →    Pin 8 (GPIO 14/TXD)   →    Serial data in
```

### 2. ADS1115 ADC Module Connections
```
ADS1115 Pin    →    Raspberry Pi 3 Pin    →    Description
VDD            →    Pin 1 (3.3V)          →    Power supply
GND            →    Pin 9 (GND)           →    Ground
SCL            →    Pin 5 (GPIO 3/SCL)    →    I2C Clock
SDA            →    Pin 3 (GPIO 2/SDA)    →    I2C Data
```

### 3. MQ137 (Ammonia) Sensor Connections
```
MQ137 Pin      →    ADS1115 Pin           →    Description
VCC            →    5V                    →    Power supply (5V)
GND            →    GND                   →    Ground
A0             →    A0 (Channel 0)        →    Analog output
```

### 4. MQ136 (H2S) Sensor Connections
```
MQ136 Pin      →    ADS1115 Pin           →    Description
VCC            →    5V                    →    Power supply (5V)
GND            →    GND                   →    Ground
A0             →    A1 (Channel 1)        →    Analog output
```

## Software Setup

### 1. Enable I2C and UART
```bash
# Enable I2C
sudo raspi-config
# Navigate to: Interfacing Options → I2C → Enable

# Enable UART
sudo raspi-config
# Navigate to: Interfacing Options → Serial → Enable

# Reboot
sudo reboot
```

### 2. Install Required Packages
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python packages
pip3 install -r requirements-simple.txt

# Install additional system packages
sudo apt install -y python3-serial python3-rpi.gpio
```

### 3. Verify Hardware Detection
```bash
# Check I2C devices
sudo i2cdetect -y 1

# Check serial devices
ls -la /dev/tty*

# Check if ADS1115 is detected (should show address 0x48)
sudo i2cdetect -y 1
```

## Testing the Sensors

### 1. Basic Test
```bash
# Run single test
python3 test_sensors.py

# Test only CO2 sensor
python3 test_sensors.py --co2-only

# Test only MQ sensors
python3 test_sensors.py --mq-only
```

### 2. Continuous Testing
```bash
# Run for 5 minutes with 10-second intervals
python3 test_sensors.py --continuous 300 --interval 10

# Run for 1 hour with 30-second intervals
python3 test_sensors.py --continuous 3600 --interval 30
```

### 3. Integration Test
```bash
# Test with the main application
python3 sensors.py --once
```

## Troubleshooting

### CO2 Sensor Issues

**Problem: CO2 sensor not detected**
```bash
# Check serial ports
ls -la /dev/tty*

# Check if device is USB or UART
dmesg | grep tty

# Test with minicom
sudo apt install minicom
sudo minicom -D /dev/ttyUSB0 -b 9600
```

**Problem: Invalid CO2 readings**
- Ensure sensor is powered for at least 2 minutes before testing
- Check wiring connections
- Verify baud rate is 9600
- Test with known good air (outdoor air should read ~400 PPM)

### MQ Sensor Issues

**Problem: ADC not detected**
```bash
# Check I2C bus
sudo i2cdetect -y 1

# Check if ADS1115 is at address 0x48
# If not found, check wiring and power
```

**Problem: MQ sensors reading 0 or very low values**
- MQ sensors need 24-48 hours to stabilize after first power-on
- Ensure 5V power supply is adequate (2A+ recommended)
- Check analog connections to ADS1115
- Verify sensor heating elements are working (sensors should be warm)

**Problem: Inconsistent readings**
- MQ sensors are sensitive to temperature and humidity
- Allow 5-10 minutes for readings to stabilize
- Take multiple readings and average them
- Ensure good ventilation around sensors

### General Issues

**Problem: Permission denied errors**
```bash
# Add user to dialout group for serial access
sudo usermod -a -G dialout $USER

# Add user to i2c group
sudo usermod -a -G i2c $USER

# Logout and login again
```

**Problem: Module not found errors**
```bash
# Install missing packages
pip3 install --upgrade pip
pip3 install -r requirements-simple.txt

# For CircuitPython packages
pip3 install adafruit-circuitpython-ads1x15
pip3 install adafruit-circuitpython-busdevice
```

## Calibration Guide

### CO2 Sensor Calibration
The MH-Z19E sensor is factory calibrated, but you can verify accuracy:
1. Test in outdoor air (should read ~400 PPM)
2. Test in a room with people (should read 800-1200 PPM)
3. Test with dry ice in a controlled environment

### MQ Sensor Calibration
MQ sensors require calibration for accurate readings:

1. **Baseline Calibration (Clean Air)**
   - Place sensors in clean outdoor air for 30 minutes
   - Record voltage readings
   - Use these as baseline values

2. **Gas Calibration**
   - For ammonia: Use household ammonia (diluted)
   - For H2S: Use rotten egg or sulfur compounds
   - Record voltage readings at known concentrations

3. **Update Conversion Formulas**
   - Modify the `convert_mq_to_ppm()` function in `sensors.py`
   - Use your calibration data to create accurate conversion curves

### Example Calibration Data
```python
# Example calibration for MQ137 (Ammonia)
def convert_mq_to_ppm(self, raw_value, voltage, sensor_type):
    if sensor_type == 'ammonia':
        # Calibrated formula based on your data
        if voltage < 0.5:
            return 0
        # Linear approximation: adjust based on your calibration
        ammonia_ppm = (voltage - 0.5) * 2000
        return max(0, ammonia_ppm)
```

## Expected Readings

### Normal Operating Ranges
- **CO2**: 400-1000 PPM (indoor), 400 PPM (outdoor)
- **Ammonia**: 0-25 PPM (normal), >25 PPM (spoiled food)
- **H2S**: 0-10 PPM (normal), >10 PPM (spoiled food)

### Warning Thresholds
- **CO2 > 1000 PPM**: Poor ventilation, check door status
- **Ammonia > 25 PPM**: Possible spoiled food
- **H2S > 10 PPM**: Possible spoiled food

## Maintenance

### Regular Checks
1. **Weekly**: Run sensor test to verify functionality
2. **Monthly**: Clean sensor surfaces (use compressed air)
3. **Quarterly**: Recalibrate MQ sensors if readings drift

### Sensor Lifespan
- **MH-Z19E**: 5+ years with proper care
- **MQ137/MQ136**: 2-3 years (heating elements degrade)
- **ADS1115**: 10+ years

### Replacement Indicators
- MQ sensors: Readings become erratic or always zero
- CO2 sensor: Consistent error messages or invalid readings
- ADC: I2C communication errors

## Safety Notes

1. **Power**: Use proper 5V 2A power supply
2. **Ventilation**: Ensure adequate ventilation around sensors
3. **Calibration**: Use proper safety equipment when calibrating with test gases
4. **Wiring**: Double-check all connections before powering on
5. **Heat**: MQ sensors get hot during operation - handle with care
