# Freezer Display Auto-Start Setup

This guide will help you set up your freezer inventory system to automatically start and display on your 5-inch LCD when your Raspberry Pi boots up.

## Quick Setup

1. **Run the setup script:**
   ```bash
   chmod +x setup_auto_display_final.sh
   ./setup_auto_display_final.sh
   ```

2. **Configure your display resolution:**
   - Edit `display_config_5inch.sh` and uncomment the resolution that matches your 5-inch display
   - Common resolutions: 800x480, 1024x600, 854x480, 1280x720

3. **Test the setup:**
   ```bash
   ./test_display.sh
   ```

4. **Reboot to test auto-start:**
   ```bash
   sudo reboot
   ```

## Files Created

- `start_pi_display_auto.sh` - Main auto-start script
- `freezer-display.service` - Systemd service for auto-start
- `freezer-display.desktop` - Desktop autostart entry
- `display_config_5inch.sh` - Display configuration for 5-inch LCDs
- `setup_auto_display_final.sh` - Complete setup script

## Manual Commands

### Start the display system:
```bash
sudo systemctl start freezer-display.service
```

### Stop the display system:
```bash
sudo systemctl stop freezer-display.service
```

### Check service status:
```bash
sudo systemctl status freezer-display.service
```

### View service logs:
```bash
sudo journalctl -u freezer-display.service -f
```

### Test display without service:
```bash
./test_display.sh
```

## Display Configuration

### Common 5-inch LCD Resolutions:
- **800x480** - Most common 5-inch resolution
- **1024x600** - Wider 5-inch displays
- **854x480** - Alternative 5-inch resolution
- **1280x720** - Larger 5-inch displays

### To configure your display:
1. Edit `display_config_5inch.sh`
2. Uncomment the resolution that matches your display
3. If you need rotation, uncomment the rotation line
4. Save and reboot

### Display Rotation Options:
- `--rotate left` - Rotate 90 degrees left
- `--rotate right` - Rotate 90 degrees right
- `--rotate inverted` - Rotate 180 degrees

## Troubleshooting

### Display not opening:
1. Check if Flask is running: `ps aux | grep python`
2. Check service status: `sudo systemctl status freezer-display.service`
3. Check logs: `sudo journalctl -u freezer-display.service -f`
4. Test manually: `./test_display.sh`

### Wrong display resolution:
1. Edit `display_config_5inch.sh`
2. Uncomment the correct resolution
3. Reboot or run: `./display_config_5inch.sh`

### Chromium not opening:
1. Install Chromium: `sudo apt install chromium-browser`
2. Check display: `echo $DISPLAY`
3. Test: `chromium-browser --version`

### Service not starting on boot:
1. Enable service: `sudo systemctl enable freezer-display.service`
2. Check dependencies: `sudo systemctl list-dependencies freezer-display.service`
3. Check if graphical.target is enabled: `sudo systemctl is-enabled graphical.target`

## Access URLs

- **Local display:** http://localhost:5000/pi
- **Network access:** http://[PI_IP]:5000/pi
- **Dashboard:** http://[PI_IP]:5000
- **Touch interface:** http://[PI_IP]:5000/touch

## Features

- ✅ Automatic startup on boot
- ✅ Fullscreen kiosk mode
- ✅ Display rotation support
- ✅ Network accessibility
- ✅ Auto-restart on failure
- ✅ Process monitoring
- ✅ Clean shutdown handling

## Support

If you encounter issues:
1. Check the service logs
2. Test with the manual test script
3. Verify your display resolution settings
4. Ensure all dependencies are installed
