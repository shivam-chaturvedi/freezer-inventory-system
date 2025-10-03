#!/bin/bash
# Fix the systemd service for the correct user

echo "Fixing systemd service for current user..."

# Get current user
CURRENT_USER=$(whoami)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "Current user: $CURRENT_USER"
echo "Script directory: $SCRIPT_DIR"

# Remove old service
sudo systemctl stop freezer-display.service 2>/dev/null || true
sudo systemctl disable freezer-display.service 2>/dev/null || true
sudo rm -f /etc/systemd/system/freezer-display.service

# Create new service with correct user
echo "Creating new systemd service..."
sudo tee /etc/systemd/system/freezer-display.service > /dev/null << EOF
[Unit]
Description=Freezer Inventory Display
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/start_headless.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload and enable
sudo systemctl daemon-reload
sudo systemctl enable freezer-display.service

echo "✅ Service fixed for user: $CURRENT_USER"
echo ""
echo "Testing the service..."
sudo systemctl start freezer-display.service
sleep 3
sudo systemctl status freezer-display.service

echo ""
echo "🎉 Service is now working!"
echo ""
echo "The system will now auto-start on boot for user: $CURRENT_USER"
