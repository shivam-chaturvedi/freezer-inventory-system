#!/usr/bin/env python3
"""
Setup script for Freezer Inventory System
This script helps with initial setup and configuration
"""

import os
import sys
import subprocess
import platform
import sqlite3
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True

def check_raspberry_pi():
    """Check if running on Raspberry Pi"""
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip()
            if 'Raspberry Pi' in model:
                print(f"✓ Running on: {model}")
                return True
    except FileNotFoundError:
        pass
    
    print("⚠ Warning: Not running on Raspberry Pi")
    print("  Sensor functionality may not work properly")
    return False

def install_dependencies():
    """Install required Python packages"""
    print("\nInstalling Python dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        return False

def setup_database():
    """Initialize the database"""
    print("\nSetting up database...")
    try:
        # Import and create database tables
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Error setting up database: {e}")
        return False

def create_desktop_shortcuts():
    """Create desktop shortcuts for easy access"""
    print("\nCreating desktop shortcuts...")
    
    desktop_path = Path.home() / "Desktop"
    if not desktop_path.exists():
        desktop_path = Path.home() / "Desktop"
        desktop_path.mkdir(exist_ok=True)
    
    # Create start script
    start_script = desktop_path / "Start Freezer System.sh"
    with open(start_script, 'w') as f:
        f.write(f"""#!/bin/bash
cd {os.getcwd()}
python3 start_freezer_system.py
""")
    start_script.chmod(0o755)
    
    # Create web dashboard shortcut
    dashboard_script = desktop_path / "Freezer Dashboard.sh"
    with open(dashboard_script, 'w') as f:
        f.write(f"""#!/bin/bash
cd {os.getcwd()}
python3 app.py &
sleep 3
xdg-open http://localhost:5000
""")
    dashboard_script.chmod(0o755)
    
    print("✓ Desktop shortcuts created")
    return True

def setup_autostart():
    """Set up autostart on boot (optional)"""
    print("\nSetting up autostart...")
    
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_file = autostart_dir / "freezer-inventory.desktop"
    with open(desktop_file, 'w') as f:
        f.write(f"""[Desktop Entry]
Type=Application
Name=Freezer Inventory System
Comment=Smart freezer inventory management
Exec=python3 {os.getcwd()}/start_freezer_system.py
Icon=applications-utilities
Terminal=false
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
""")
    
    print("✓ Autostart configured")
    print("  To disable autostart, delete the desktop file:")
    print(f"  rm {desktop_file}")
    return True

def setup_gpio_permissions():
    """Set up GPIO permissions for non-root user"""
    print("\nSetting up GPIO permissions...")
    
    # Add user to gpio group
    try:
        subprocess.run(['sudo', 'usermod', '-a', '-G', 'gpio', os.getenv('USER')], check=True)
        print("✓ User added to gpio group")
        print("  Note: You may need to log out and back in for changes to take effect")
    except subprocess.CalledProcessError:
        print("⚠ Could not add user to gpio group")
        print("  You may need to run the system with sudo for GPIO access")
    
    return True

def create_config_file():
    """Create a default configuration file"""
    print("\nCreating configuration file...")
    
    config_content = """# Freezer Inventory System Configuration
# Edit these values as needed

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///freezer_inventory.db

# Sensor Configuration
DHT_PIN=4
DOOR_SENSOR_PIN=18
LIGHT_SENSOR_PIN=24

# Monitoring Configuration
SENSOR_INTERVAL=30
TEMP_WARNING_THRESHOLD=4
HUMIDITY_WARNING_THRESHOLD=80

# Web Interface Configuration
WEB_HOST=0.0.0.0
WEB_PORT=5000
"""
    
    with open('.env', 'w') as f:
        f.write(config_content)
    
    print("✓ Configuration file created (.env)")
    return True

def test_system():
    """Test the system components"""
    print("\nTesting system components...")
    
    # Test Flask app
    try:
        from app import app
        print("✓ Flask app imports successfully")
    except Exception as e:
        print(f"✗ Flask app test failed: {e}")
        return False
    
    # Test sensor module
    try:
        import sensors
        print("✓ Sensor module imports successfully")
    except Exception as e:
        print(f"✗ Sensor module test failed: {e}")
        return False
    
    # Test database
    try:
        from app import db
        with app.app_context():
            db.create_all()
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False
    
    print("✓ All system tests passed")
    return True

def main():
    """Main setup function"""
    print("=== Freezer Inventory System Setup ===")
    print("This script will help you set up the freezer inventory system")
    print()
    
    # Check system requirements
    if not check_python_version():
        return False
    
    check_raspberry_pi()
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create configuration file
    create_config_file()
    
    # Setup database
    if not setup_database():
        return False
    
    # Setup GPIO permissions
    setup_gpio_permissions()
    
    # Create desktop shortcuts
    create_desktop_shortcuts()
    
    # Ask about autostart
    response = input("\nWould you like to enable autostart on boot? (y/n): ").lower()
    if response in ['y', 'yes']:
        setup_autostart()
    
    # Test system
    if not test_system():
        print("\n⚠ Some tests failed, but you can still try running the system")
    
    print("\n=== Setup Complete ===")
    print("You can now start the system using:")
    print("  python3 start_freezer_system.py")
    print()
    print("Or use the desktop shortcuts:")
    print("  - Start Freezer System.sh")
    print("  - Freezer Dashboard.sh")
    print()
    print("Web interfaces will be available at:")
    print("  - Dashboard: http://localhost:5000")
    print("  - Touch Interface: http://localhost:5000/touch")
    print()
    print("For hardware setup instructions, see README.md")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during setup: {e}")
        sys.exit(1)

