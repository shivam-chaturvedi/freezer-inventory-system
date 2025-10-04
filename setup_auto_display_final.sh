#!/bin/bash
# Complete setup script for auto-starting freezer display on 5-inch LCD

echo "=== Freezer Display Auto-Start Setup ==="
echo "Setting up automatic display startup for 5-inch LCD..."

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Make scripts executable
echo "Making scripts executable..."
chmod +x start_pi_display_auto.sh
chmod +x start_pi_display_final.sh
chmod +x start_pi_display.sh

# Install systemd service
echo "Installing systemd service..."
sudo cp freezer-display.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable freezer-display.service

# Install desktop autostart entry
echo "Installing desktop autostart entry..."
mkdir -p /home/pi/.config/autostart
cp freezer-display.desktop /home/pi/.config/autostart/
chown pi:pi /home/pi/.config/autostart/freezer-display.desktop

# Configure display settings for 5-inch LCD
echo "Configuring display settings..."

# Create display configuration script
cat > configure_display.sh << 'EOF'
#!/bin/bash
# Display configuration for 5-inch LCD

# Wait for X server to start
sleep 10

# Set display environment
export DISPLAY=:0

# Common 5-inch display resolutions and settings
# Uncomment the one that matches your display:

# For 800x480 displays (most common 5-inch)
# xrandr --output HDMI-1 --mode 800x480 --rotate normal

# For 1024x600 displays
# xrandr --output HDMI-1 --mode 1024x600 --rotate normal

# For 854x480 displays
# xrandr --output HDMI-1 --mode 854x480 --rotate normal

# For 1280x720 displays (larger 5-inch)
# xrandr --output HDMI-1 --mode 1280x720 --rotate normal

# If you need to rotate the display 90 degrees:
# xrandr --output HDMI-1 --rotate left
# xrandr --output HDMI-1 --rotate right

# If you need to rotate 180 degrees:
# xrandr --output HDMI-1 --rotate inverted

echo "Display configuration applied"
EOF

chmod +x configure_display.sh

# Add display configuration to autostart
echo "Adding display configuration to autostart..."
cat > /home/pi/.config/autostart/configure-display.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Configure Display
Comment=Configure display for 5-inch LCD
Exec=/home/pi/freezer-inventory-system/configure_display.sh
Icon=preferences-desktop-display
Terminal=false
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=5
StartupNotify=false
EOF

chown pi:pi /home/pi/.config/autostart/configure-display.desktop

# Install Chromium if not already installed
echo "Installing Chromium browser..."
sudo apt update
sudo apt install -y chromium-browser

# Configure Chromium for kiosk mode
echo "Configuring Chromium for kiosk mode..."
mkdir -p /home/pi/.config/chromium/Default
cat > /home/pi/.config/chromium/Default/Preferences << 'EOF'
{
   "browser": {
      "check_default_browser": false
   },
   "profile": {
      "default_content_setting_values": {
         "notifications": 2
      }
   },
   "translate": {
      "enabled": false
   }
}
EOF

chown -R pi:pi /home/pi/.config/chromium

# Create a test script
echo "Creating test script..."
cat > test_display.sh << 'EOF'
#!/bin/bash
echo "Testing display setup..."
echo "Starting Flask application..."
python3 app.py &
FLASK_PID=$!
sleep 5

if ps -p $FLASK_PID > /dev/null; then
    echo "✅ Flask started successfully"
    echo "Opening display in 3 seconds..."
    sleep 3
    chromium-browser --kiosk --disable-infobars --disable-session-crashed-bubble --disable-web-security --user-data-dir=/tmp/chrome_test --no-first-run --no-default-browser-check "http://localhost:5000/pi" &
    echo "✅ Display should now be open"
    echo "Press Ctrl+C to stop the test"
    wait $FLASK_PID
else
    echo "❌ Failed to start Flask"
fi
EOF

chmod +x test_display.sh

# Create a stop script
echo "Creating stop script..."
cat > stop_display.sh << 'EOF'
#!/bin/bash
echo "Stopping freezer display system..."
sudo systemctl stop freezer-display.service
pkill -f "python.*app.py"
pkill -f "chromium"
echo "Display system stopped"
EOF

chmod +x stop_display.sh

# Create a restart script
echo "Creating restart script..."
cat > restart_display.sh << 'EOF'
#!/bin/bash
echo "Restarting freezer display system..."
./stop_display.sh
sleep 2
sudo systemctl start freezer-display.service
echo "Display system restarted"
EOF

chmod +x restart_display.sh

echo ""
echo "=== Setup Complete ==="
echo ""
echo "✅ Systemd service installed and enabled"
echo "✅ Desktop autostart configured"
echo "✅ Display configuration ready"
echo "✅ Chromium configured for kiosk mode"
echo ""
echo "Available commands:"
echo "  ./test_display.sh     - Test the display setup"
echo "  ./stop_display.sh     - Stop the display system"
echo "  ./restart_display.sh  - Restart the display system"
echo ""
echo "To start the service now:"
echo "  sudo systemctl start freezer-display.service"
echo ""
echo "To check service status:"
echo "  sudo systemctl status freezer-display.service"
echo ""
echo "To view service logs:"
echo "  sudo journalctl -u freezer-display.service -f"
echo ""
echo "The display will now automatically start when your Pi boots up!"
echo "Make sure to:"
echo "1. Configure the correct display resolution in configure_display.sh"
echo "2. Test the setup with ./test_display.sh"
echo "3. Reboot your Pi to test auto-start"
