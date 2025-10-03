# Freezer Inventory System

A smart inventory management system for your freezer with real-time sensor monitoring and touch interface.

## Features

- **Web Dashboard**: View inventory and sensor data from any device
- **Touch Interface**: Easy-to-use interface for adding items directly at the freezer
- **Sensor Monitoring**: Temperature, humidity, and door status monitoring
- **Spoilage Detection**: Automatic detection of potentially spoiled items
- **Real-time Updates**: Live data updates every 30 seconds

## Hardware Requirements

- Raspberry Pi 3 (or newer)
- 5-inch DSI LCD capacitive touch screen
- DHT22 temperature and humidity sensor
- Magnetic door sensor (reed switch)
- Optional: Light sensor (LDR)

## Hardware Setup

### Sensor Connections

1. **DHT22 Sensor** (Temperature & Humidity)
   - VCC → 3.3V
   - Data → GPIO 4
   - GND → Ground

2. **Door Sensor** (Magnetic Switch)
   - One wire → GPIO 18
   - Other wire → Ground

3. **Light Sensor** (Optional LDR)
   - One wire → GPIO 24
   - Other wire → Ground

### Touch Screen Setup

1. Enable DSI interface in Raspberry Pi configuration
2. Install touch screen drivers if needed
3. Configure display resolution for optimal touch experience

## Software Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd freezer-inventory-system
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**
   ```bash
   python app.py
   # This will create the SQLite database automatically
   ```

## Usage

### Starting the System

1. **Start the complete system** (recommended):
   ```bash
   python start_freezer_system.py
   ```

2. **Or start components separately**:
   ```bash
   # Terminal 1 - Web server
   python app.py
   
   # Terminal 2 - Sensor monitoring
   python sensors.py
   ```

### Accessing the Interfaces

- **Web Dashboard**: http://localhost:5000
- **Touch Interface**: http://localhost:5000/touch

### Adding Items

1. **Via Touch Interface** (at the freezer):
   - Open the touch interface on the display
   - Fill in item details
   - Select category using the touch buttons
   - Tap "Save to Freezer"

2. **Via Web Dashboard** (from any device):
   - Open the web dashboard
   - Click "Add Item" button
   - Fill in the form and submit

### Monitoring Sensors

The system automatically monitors:
- **Temperature**: Alerts if above 4°C (unsafe for refrigeration)
- **Humidity**: Alerts if above 80% (high humidity can cause spoilage)
- **Door Status**: Alerts if door is left open

## Configuration

### Sensor Settings

Edit `sensors.py` to modify:
- GPIO pin assignments
- Sensor reading intervals
- Alert thresholds

### Web Interface

Edit `app.py` to modify:
- Database settings
- API endpoints
- Spoilage detection logic

## Troubleshooting

### Common Issues

1. **Sensors not reading**:
   - Check GPIO connections
   - Verify sensor power supply
   - Check for loose connections

2. **Touch screen not responsive**:
   - Calibrate touch screen
   - Check display drivers
   - Verify touch screen configuration

3. **Web interface not accessible**:
   - Check if Flask app is running
   - Verify port 5000 is not blocked
   - Check firewall settings

### Logs

- Flask app logs: Check terminal output
- Sensor logs: Check terminal output or system logs
- Database: SQLite file `freezer_inventory.db`

## API Endpoints

### Inventory
- `GET /api/inventory` - Get all inventory items
- `POST /api/inventory` - Add new item
- `PUT /api/inventory/<id>` - Update item
- `DELETE /api/inventory/<id>` - Delete item

### Sensors
- `GET /api/sensors` - Get latest sensor data
- `POST /api/sensors` - Add sensor reading
- `GET /api/sensors/history` - Get sensor history

### Spoilage Detection
- `GET /api/check_spoilage` - Check for spoiled items

## Development

### Adding New Sensors

1. Add sensor reading method to `FreezerSensors` class
2. Update `read_all_sensors()` method
3. Add sensor data to database model
4. Update web interface to display new sensor data

### Customizing the Interface

- **Dashboard**: Edit `templates/dashboard.html` and `static/css/dashboard.css`
- **Touch Interface**: Edit `templates/touch_interface.html` and `static/css/touch.css`
- **JavaScript**: Edit `static/js/dashboard.js` and `static/js/touch.js`

## License

This project is open source. Feel free to modify and distribute.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Verify hardware connections
4. Check software dependencies

