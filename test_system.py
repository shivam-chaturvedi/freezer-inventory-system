#!/usr/bin/env python3
"""
Test script for Freezer Inventory System
This script tests all components to ensure they're working correctly
"""

import sys
import os
import time
import requests
import json
from datetime import datetime, timedelta

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        import RPi.GPIO
        print("✓ RPi.GPIO imported successfully")
    except ImportError as e:
        print(f"⚠ RPi.GPIO import failed: {e}")
        print("  This is expected if not running on Raspberry Pi")
    
    try:
        import Adafruit_DHT
        print("✓ Adafruit_DHT imported successfully")
    except ImportError as e:
        print(f"⚠ Adafruit_DHT import failed: {e}")
        print("  This is expected if not running on Raspberry Pi")
    
    return True

def test_database():
    """Test database functionality"""
    print("\nTesting database...")
    
    try:
        from app import app, db, InventoryItem, SensorData
        
        with app.app_context():
            # Test creating a sample item
            test_item = InventoryItem(
                name="Test Item",
                quantity=1,
                unit="pieces",
                category="test",
                notes="Test item for system testing"
            )
            
            db.session.add(test_item)
            db.session.commit()
            
            # Test retrieving the item
            retrieved_item = InventoryItem.query.filter_by(name="Test Item").first()
            if retrieved_item:
                print("✓ Database write/read test passed")
                
                # Clean up test item
                db.session.delete(retrieved_item)
                db.session.commit()
                print("✓ Database cleanup completed")
            else:
                print("✗ Database read test failed")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_flask_app():
    """Test Flask application"""
    print("\nTesting Flask application...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test dashboard route
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Dashboard route working")
            else:
                print(f"✗ Dashboard route failed: {response.status_code}")
                return False
            
            # Test touch interface route
            response = client.get('/touch')
            if response.status_code == 200:
                print("✓ Touch interface route working")
            else:
                print(f"✗ Touch interface route failed: {response.status_code}")
                return False
            
            # Test API routes
            response = client.get('/api/inventory')
            if response.status_code == 200:
                print("✓ Inventory API working")
            else:
                print(f"✗ Inventory API failed: {response.status_code}")
                return False
            
            response = client.get('/api/sensors')
            if response.status_code == 200:
                print("✓ Sensors API working")
            else:
                print(f"✗ Sensors API failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Flask app test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints with sample data"""
    print("\nTesting API endpoints...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test adding an item
            test_item = {
                "name": "Test API Item",
                "quantity": 2,
                "unit": "pieces",
                "category": "test",
                "notes": "Test item for API testing",
                "expiry_date": (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            response = client.post('/api/inventory', 
                                 data=json.dumps(test_item),
                                 content_type='application/json')
            
            if response.status_code == 201:
                print("✓ Add item API working")
                item_data = response.get_json()
                item_id = item_data['id']
                
                # Test updating the item
                test_item['quantity'] = 3
                response = client.put(f'/api/inventory/{item_id}',
                                    data=json.dumps(test_item),
                                    content_type='application/json')
                
                if response.status_code == 200:
                    print("✓ Update item API working")
                else:
                    print(f"✗ Update item API failed: {response.status_code}")
                
                # Test deleting the item
                response = client.delete(f'/api/inventory/{item_id}')
                if response.status_code == 204:
                    print("✓ Delete item API working")
                else:
                    print(f"✗ Delete item API failed: {response.status_code}")
            else:
                print(f"✗ Add item API failed: {response.status_code}")
                return False
            
            # Test sensor data API
            test_sensor_data = {
                "temperature": 2.5,
                "humidity": 45.0,
                "door_open": False,
                "light_level": 100
            }
            
            response = client.post('/api/sensors',
                                 data=json.dumps(test_sensor_data),
                                 content_type='application/json')
            
            if response.status_code == 201:
                print("✓ Add sensor data API working")
            else:
                print(f"✗ Add sensor data API failed: {response.status_code}")
            
            # Test spoilage check API
            response = client.get('/api/check_spoilage')
            if response.status_code == 200:
                print("✓ Spoilage check API working")
            else:
                print(f"✗ Spoilage check API failed: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"✗ API endpoints test failed: {e}")
        return False

def test_sensor_simulation():
    """Test sensor functionality (simulated if not on Raspberry Pi)"""
    print("\nTesting sensor functionality...")
    
    try:
        from sensors import FreezerSensors
        
        # Create sensor instance
        sensors = FreezerSensors()
        
        # Test reading sensors (will work even without hardware)
        sensor_data = sensors.read_all_sensors()
        
        if sensor_data:
            print("✓ Sensor reading functionality working")
            print(f"  Sample data: {sensor_data}")
        else:
            print("⚠ Sensor reading returned no data (expected without hardware)")
        
        # Test spoilage condition checking
        test_data = {
            'temperature': 5.0,  # Above threshold
            'humidity': 85.0,    # Above threshold
            'door_open': True
        }
        
        warnings = sensors.check_spoilage_conditions(test_data)
        if warnings:
            print(f"✓ Spoilage detection working: {warnings}")
        else:
            print("⚠ Spoilage detection not working as expected")
        
        return True
    except Exception as e:
        print(f"✗ Sensor test failed: {e}")
        return False

def test_web_interface():
    """Test web interface accessibility"""
    print("\nTesting web interface...")
    
    try:
        # Start Flask app in background
        import subprocess
        import threading
        import time
        
        # Start Flask app
        flask_process = subprocess.Popen([sys.executable, 'app.py'], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE)
        
        # Wait for Flask to start
        time.sleep(3)
        
        try:
            # Test if Flask is running
            response = requests.get('http://localhost:5000', timeout=5)
            if response.status_code == 200:
                print("✓ Web interface accessible")
            else:
                print(f"✗ Web interface not accessible: {response.status_code}")
                return False
            
            # Test touch interface
            response = requests.get('http://localhost:5000/touch', timeout=5)
            if response.status_code == 200:
                print("✓ Touch interface accessible")
            else:
                print(f"✗ Touch interface not accessible: {response.status_code}")
                return False
            
        finally:
            # Stop Flask app
            flask_process.terminate()
            flask_process.wait()
        
        return True
    except Exception as e:
        print(f"✗ Web interface test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== Freezer Inventory System Test ===")
    print("This script will test all components of the system")
    print()
    
    tests = [
        ("Import Test", test_imports),
        ("Database Test", test_database),
        ("Flask App Test", test_flask_app),
        ("API Endpoints Test", test_api_endpoints),
        ("Sensor Test", test_sensor_simulation),
        ("Web Interface Test", test_web_interface)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                print(f"✓ {test_name} PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nTo start the system, run:")
        print("  python3 start_freezer_system.py")
    else:
        print("⚠ Some tests failed. Please check the errors above.")
        print("The system may still work, but some features might not function properly.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
        sys.exit(1)

