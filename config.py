"""
Configuration file for Freezer Inventory System
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///freezer_inventory.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Sensor Configuration
    DHT_PIN = int(os.environ.get('DHT_PIN', 4))
    DOOR_SENSOR_PIN = int(os.environ.get('DOOR_SENSOR_PIN', 18))
    LIGHT_SENSOR_PIN = int(os.environ.get('LIGHT_SENSOR_PIN', 24))
    
    # Monitoring Configuration
    SENSOR_INTERVAL = int(os.environ.get('SENSOR_INTERVAL', 30))
    TEMP_WARNING_THRESHOLD = float(os.environ.get('TEMP_WARNING_THRESHOLD', 4.0))
    HUMIDITY_WARNING_THRESHOLD = float(os.environ.get('HUMIDITY_WARNING_THRESHOLD', 80.0))
    
    # Web Interface Configuration
    WEB_HOST = os.environ.get('WEB_HOST', '0.0.0.0')
    WEB_PORT = int(os.environ.get('WEB_PORT', 5000))
    
    # Spoilage Detection
    EXPIRY_WARNING_DAYS = 3  # Days before expiry to show warning
    TEMP_SPOILAGE_THRESHOLD = 4.0  # Temperature above which items may spoil
    HUMIDITY_SPOILAGE_THRESHOLD = 80.0  # Humidity above which items may spoil

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

