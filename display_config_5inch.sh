#!/bin/bash
# Display configuration for 5-inch LCD displays
# This script configures the display resolution and rotation

echo "Configuring display for 5-inch LCD..."

# Wait for X server to be ready
sleep 5

# Set display environment
export DISPLAY=:0

# Get available display outputs
echo "Available display outputs:"
xrandr --query | grep " connected"

# Common 5-inch display configurations
# Uncomment the configuration that matches your display:

# Configuration 1: 800x480 (most common 5-inch resolution)
echo "Setting up 800x480 resolution..."
xrandr --output HDMI-1 --mode 800x480 --rotate normal 2>/dev/null || \
xrandr --output HDMI-A-1 --mode 800x480 --rotate normal 2>/dev/null || \
xrandr --output DSI-1 --mode 800x480 --rotate normal 2>/dev/null || \
echo "Could not set 800x480, trying other resolutions..."

# Configuration 2: 1024x600 (wider 5-inch displays)
# xrandr --output HDMI-1 --mode 1024x600 --rotate normal 2>/dev/null || \
# xrandr --output HDMI-A-1 --mode 1024x600 --rotate normal 2>/dev/null || \
# xrandr --output DSI-1 --mode 1024x600 --rotate normal 2>/dev/null

# Configuration 3: 854x480 (alternative 5-inch resolution)
# xrandr --output HDMI-1 --mode 854x480 --rotate normal 2>/dev/null || \
# xrandr --output HDMI-A-1 --mode 854x480 --rotate normal 2>/dev/null || \
# xrandr --output DSI-1 --mode 854x480 --rotate normal 2>/dev/null

# Configuration 4: 1280x720 (larger 5-inch displays)
# xrandr --output HDMI-1 --mode 1280x720 --rotate normal 2>/dev/null || \
# xrandr --output HDMI-A-1 --mode 1280x720 --rotate normal 2>/dev/null || \
# xrandr --output DSI-1 --mode 1280x720 --rotate normal 2>/dev/null

# If you need to rotate the display, uncomment one of these:
# xrandr --output HDMI-1 --rotate left    # Rotate 90 degrees left
# xrandr --output HDMI-1 --rotate right   # Rotate 90 degrees right
# xrandr --output HDMI-1 --rotate inverted # Rotate 180 degrees

# Set brightness (adjust as needed for your display)
# echo 80 > /sys/class/backlight/*/brightness 2>/dev/null || true

# Disable screen blanking
xset s off
xset -dpms
xset s noblank

echo "Display configuration completed"
echo "Current display settings:"
xrandr --query | grep -A 1 " connected"
