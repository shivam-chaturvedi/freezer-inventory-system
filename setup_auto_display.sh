#!/bin/bash
# Setup auto-run for Pi display

echo "Setting up auto-run for Pi display..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create a desktop entry for auto-start
echo "Creating desktop entry..."
cat > ~/.config/autostart/freezer-display.desktop << EOF
[Desktop Entry]
Type=Application
Name=Freezer Display
Comment=Smart freezer inventory display
Exec=$SCRIPT_DIR/start_headless.sh
Icon=applications-utilities
Terminal=false
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

# Make it executable
chmod +x ~/.config/autostart/freezer-display.desktop

# Create a systemd service for better control
echo "Creating systemd service..."
sudo tee /etc/systemd/system/freezer-display.service > /dev/null << EOF
[Unit]
Description=Freezer Inventory Display
After=network.target graphical.target
Wants=graphical.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/start_headless.sh
Restart=always
RestartSec=10
Environment=DISPLAY=:0

[Install]
WantedBy=graphical.target
EOF

# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable freezer-display.service

# Create a simple display launcher
echo "Creating display launcher..."
cat > ~/Desktop/Freezer\ Display.sh << EOF
#!/bin/bash
cd $SCRIPT_DIR
./start_headless.sh
EOF
chmod +x ~/Desktop/Freezer\ Display.sh

# Create a browser launcher for the display
echo "Creating browser launcher..."
cat > ~/Desktop/Open\ Freezer\ Display.sh << EOF
#!/bin/bash
# Get Pi IP
PI_IP=\$(hostname -I | awk '{print \$1}')

# Try different browsers
if command -v chromium &> /dev/null; then
    chromium --kiosk --disable-infobars --disable-session-crashed-bubble --disable-web-security --user-data-dir=/tmp/chrome_temp --no-first-run --no-default-browser-check "http://\$PI_IP:5000/pi" &
elif command -v firefox &> /dev/null; then
    firefox --kiosk "http://\$PI_IP:5000/pi" &
elif command -v midori &> /dev/null; then
    midori -e Fullscreen -a "http://\$PI_IP:5000/pi" &
else
    echo "No browser found. Please install one:"
    echo "sudo apt install chromium-browser"
    echo "sudo apt install firefox"
    echo "sudo apt install midori"
fi
EOF
chmod +x ~/Desktop/Open\ Freezer\ Display.sh

echo ""
echo "✅ Auto-run setup complete!"
echo ""
echo "🔄 The system will now:"
echo "   • Start automatically on boot"
echo "   • Run the Flask server"
echo "   • Be ready for your display"
echo ""
echo "🖥️  To open the display:"
echo "   • Double-click 'Open Freezer Display.sh' on desktop"
echo "   • Or open browser and go to: http://$(hostname -I | awk '{print $1}'):5000/pi"
echo ""
echo "⚙️  Service controls:"
echo "   • Start: sudo systemctl start freezer-display.service"
echo "   • Stop: sudo systemctl stop freezer-display.service"
echo "   • Status: sudo systemctl status freezer-display.service"
echo "   • Disable: sudo systemctl disable freezer-display.service"
echo ""
echo "🎉 Your freezer system will now auto-start on boot!"
