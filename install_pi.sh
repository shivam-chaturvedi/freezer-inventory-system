#!/bin/bash
# Installation script for Raspberry Pi

echo "=== Freezer Inventory System Installation ==="
echo "Installing on Raspberry Pi..."

# Update system packages
echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install required system packages
echo "Installing system dependencies..."
sudo apt install -y python3-pip python3-venv python3-full git

# Install I2C tools and libraries
echo "Installing I2C tools..."
sudo apt install -y i2c-tools python3-smbus

# Enable I2C interface
echo "Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv freezer_env
source freezer_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Set up database
echo "Setting up database..."
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"

# Create startup script
echo "Creating startup script..."
cat > start_freezer.sh << 'EOF'
#!/bin/bash
cd /home/pi/freezer-inventory-system
source freezer_env/bin/activate
python3 start_freezer_system.py
EOF

chmod +x start_freezer.sh

# Create systemd service for autostart
echo "Creating systemd service..."
sudo tee /etc/systemd/system/freezer-inventory.service > /dev/null << EOF
[Unit]
Description=Freezer Inventory System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/freezer-inventory-system
ExecStart=/home/pi/freezer-inventory-system/freezer_env/bin/python start_freezer_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable freezer-inventory.service

echo "=== Installation Complete ==="
echo ""
echo "To start the system manually:"
echo "  ./start_freezer.sh"
echo ""
echo "To start the service:"
echo "  sudo systemctl start freezer-inventory.service"
echo ""
echo "To check service status:"
echo "  sudo systemctl status freezer-inventory.service"
echo ""
echo "Web interfaces will be available at:"
echo "  - Dashboard: http://localhost:5000"
echo "  - Touch Interface: http://localhost:5000/touch"
echo ""
echo "Hardware connections:"
echo "  - MH-Z19E CO2 sensor: USB port"
echo "  - MQ137 (Ammonia): ADS1115 Channel 0"
echo "  - MQ136 (H2S): ADS1115 Channel 1"
echo "  - Door sensor: GPIO 18"
echo "  - ADS1115: I2C (SDA/SCL pins)"
