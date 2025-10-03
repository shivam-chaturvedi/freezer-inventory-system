#!/bin/bash
# Installation script for Pi Display System

echo "=== Freezer Pi Display Installation ==="
echo "Installing display system for 5-inch touch screen..."

# Update system packages
echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install required system packages
echo "Installing system dependencies..."
sudo apt install -y python3-pip python3-venv python3-full git chromium-browser

# Install I2C tools and libraries
echo "Installing I2C tools..."
sudo apt install -y i2c-tools python3-smbus

# Enable I2C interface
echo "Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Enable auto-login for pi user
echo "Enabling auto-login..."
sudo raspi-config nonint do_boot_behaviour B4

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv freezer_env
source freezer_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements-simple.txt

# Set up database
echo "Setting up database..."
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"

# Make scripts executable
echo "Making scripts executable..."
chmod +x start_pi_display.sh
chmod +x start_freezer.sh

# Install systemd service
echo "Installing systemd service..."
sudo cp freezer-display.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable freezer-display.service

# Create desktop shortcut
echo "Creating desktop shortcut..."
cat > ~/Desktop/Freezer\ Display.sh << 'EOF'
#!/bin/bash
cd /home/pi/freezer-inventory-system
./start_pi_display.sh
EOF
chmod +x ~/Desktop/Freezer\ Display.sh

echo "=== Installation Complete ==="
echo ""
echo "The system will automatically start on boot and display the freezer interface."
echo ""
echo "Manual controls:"
echo "  - Start display: ./start_pi_display.sh"
echo "  - Start service: sudo systemctl start freezer-display.service"
echo "  - Stop service: sudo systemctl stop freezer-display.service"
echo "  - Check status: sudo systemctl status freezer-display.service"
echo ""
echo "Display will be available at:"
echo "  - Pi Display: http://localhost:5000/pi"
echo "  - Web Dashboard: http://localhost:5000"
echo "  - Touch Interface: http://localhost:5000/touch"
echo ""
echo "Hardware connections:"
echo "  - MH-Z19E CO2 sensor: USB port"
echo "  - MQ137 (Ammonia): ADS1115 Channel 0"
echo "  - MQ136 (H2S): ADS1115 Channel 1"
echo "  - Door sensor: GPIO 18"
echo "  - ADS1115: I2C (SDA/SCL pins)"
echo ""
echo "The system will restart automatically to enable the display service."
echo "Press Enter to continue with restart, or Ctrl+C to cancel..."
read

# Restart the system
echo "Restarting system to enable display service..."
sudo reboot
