# Raspberry Pi Setup Guide

## 🎯 **Your System is Working Perfectly!**

The Flask server is running successfully and the database is fixed. The X11 errors you see are normal for headless systems - they don't affect functionality.

## 🚀 **Quick Start:**

```bash
# 1. Pull latest changes
git pull origin main

# 2. Start the system (headless mode)
chmod +x start_headless.sh
./start_headless.sh
```

## 📱 **Access Your Freezer System:**

Once running, open these URLs in any browser:

- **Pi Display**: `http://192.168.1.223:5000/pi` (for your 5-inch display)
- **Web Dashboard**: `http://192.168.1.223:5000` (for other devices)
- **Touch Interface**: `http://192.168.1.223:5000/touch` (original interface)

## 🖥️ **For Your 5-Inch Display:**

1. **Connect your display** to the Pi
2. **Open a browser** (Chromium, Firefox, etc.)
3. **Go to**: `http://192.168.1.223:5000/pi`
4. **Press F11** for fullscreen mode
5. **Enjoy your professional freezer interface!**

## 🔧 **Hardware Setup:**

### **Sensor Connections:**
- **MH-Z19E CO2**: USB port (plug and play)
- **MQ137 (Ammonia)**: ADS1115 Channel 0 (A0)
- **MQ136 (H2S)**: ADS1115 Channel 1 (A1)
- **Door Sensor**: GPIO 18
- **ADS1115**: I2C (SDA/SCL pins)

### **Display Setup:**
- **5-inch DSI LCD**: Connect to Pi's DSI port
- **Enable DSI**: `sudo raspi-config` → Advanced Options → DSI
- **Calibrate touch**: If needed, run touch calibration

## 📊 **System Features:**

✅ **Professional Pi Display** - Optimized for 5-inch screen  
✅ **Inventory Management** - Add, edit, delete items  
✅ **Sensor Monitoring** - CO2, Ammonia, H2S, Air Quality  
✅ **Spoilage Detection** - Automatic alerts  
✅ **Touch Interface** - Easy item addition  
✅ **Web Dashboard** - Access from any device  
✅ **Auto-start** - Runs on boot  

## 🛠️ **Troubleshooting:**

### **If display doesn't work:**
```bash
# Check if Flask is running
ps aux | grep python

# Check port 5000
netstat -tlnp | grep 5000

# Restart system
./stop_flask.sh
./start_headless.sh
```

### **If sensors don't work:**
```bash
# Enable I2C
sudo raspi-config
# Go to: Interfacing Options → I2C → Enable

# Check I2C devices
sudo i2cdetect -y 1
```

## 🎉 **You're All Set!**

Your freezer inventory system is now running perfectly. The professional interface will work great on your 5-inch display once you connect it and open the browser!
