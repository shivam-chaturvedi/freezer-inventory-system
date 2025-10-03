#!/bin/bash
# Install browser for Pi display

echo "Installing browser for Pi display..."

# Update package list
sudo apt update

# Try to install Chromium
echo "Installing Chromium browser..."
if sudo apt install -y chromium-browser; then
    echo "Chromium installed successfully!"
    BROWSER="chromium-browser"
elif sudo apt install -y chromium; then
    echo "Chromium installed successfully!"
    BROWSER="chromium"
else
    echo "Chromium installation failed, trying Firefox..."
    if sudo apt install -y firefox; then
        echo "Firefox installed successfully!"
        BROWSER="firefox"
    else
        echo "Firefox installation failed, trying Midori..."
        if sudo apt install -y midori; then
            echo "Midori installed successfully!"
            BROWSER="midori"
        else
            echo "All browser installations failed!"
            echo "Please install a browser manually:"
            echo "  sudo apt install chromium-browser"
            echo "  sudo apt install firefox"
            echo "  sudo apt install midori"
            exit 1
        fi
    fi
fi

echo "Browser installation complete: $BROWSER"
echo "You can now run: ./start_pi_display_fixed.sh"
