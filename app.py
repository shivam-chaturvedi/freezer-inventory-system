from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import qrcode
from io import BytesIO
import base64

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Supabase configuration
SUPABASE_URL = "https://jabnieuqwrupzycmvbmh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImphYm5pZXVxd3J1cHp5Y212Ym1oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA1ODQ2NTcsImV4cCI6MjA3NjE2MDY1N30.Gh3wQMDs1zXv6t5Fx6OyDYZEldBhGqeQNa9Gkw--mqw"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Helper functions
def generate_qr_code(data):
    """Generate QR code for inventory item"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

def format_item(item):
    """Format item from Supabase to match expected structure"""
    return {
        'id': item['id'],
        'name': item['name'],
        'quantity': item['quantity'],
        'unit': item['unit'],
        'added_date': item['added_date'],
        'expiry_date': item['expiry_date'],
        'category': item['category'],
        'notes': item['notes'],
        'is_spoiled': item['is_spoiled'],
        'qr_code': item.get('qr_code')
    }

def format_sensor(sensor):
    """Format sensor data from Supabase"""
    return {
        'id': sensor['id'],
        'timestamp': sensor['timestamp'],
        'co2_ppm': sensor['co2_ppm'],
        'ammonia_ppm': sensor['ammonia_ppm'],
        'h2s_ppm': sensor['h2s_ppm'],
        'door_open': sensor['door_open'],
        'air_quality': sensor['air_quality']
    }

# Routes
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/touch')
def touch_interface():
    return render_template('touch_interface.html')

@app.route('/pi')
def pi_display():
    return render_template('pi_display.html')


@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    try:
        response = supabase.table('inventory_item').select('*').order('added_date', desc=True).execute()
        items = [format_item(item) for item in response.data]
        return jsonify(items)
    except Exception as e:
        print(f"Error fetching inventory: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory', methods=['POST'])
def add_inventory_item():
    try:
        data = request.get_json()
        
        # Generate QR code for the item
        qr_data = f"{data['name']}-{data['quantity']}{data['unit']}"
        qr_code = generate_qr_code(qr_data)
        
        item_data = {
            'name': data['name'],
            'quantity': data['quantity'],
            'unit': data['unit'],
            'category': data.get('category', ''),
            'notes': data.get('notes', ''),
            'expiry_date': data.get('expiry_date'),
            'qr_code': qr_code
        }
        
        response = supabase.table('inventory_item').insert(item_data).execute()
        
        if response.data:
            return jsonify(format_item(response.data[0])), 201
        else:
            return jsonify({'error': 'Failed to create item'}), 500
            
    except Exception as e:
        print(f"Error adding inventory item: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/<int:item_id>', methods=['PUT'])
def update_inventory_item(item_id):
    try:
        data = request.get_json()
        
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name']
        if 'quantity' in data:
            update_data['quantity'] = data['quantity']
        if 'unit' in data:
            update_data['unit'] = data['unit']
        if 'category' in data:
            update_data['category'] = data['category']
        if 'notes' in data:
            update_data['notes'] = data['notes']
        if 'is_spoiled' in data:
            update_data['is_spoiled'] = data['is_spoiled']
        if 'expiry_date' in data:
            update_data['expiry_date'] = data['expiry_date']
        
        response = supabase.table('inventory_item').update(update_data).eq('id', item_id).execute()
        
        if response.data:
            return jsonify(format_item(response.data[0]))
        else:
            return jsonify({'error': 'Item not found'}), 404
            
    except Exception as e:
        print(f"Error updating inventory item: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/<int:item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    try:
        response = supabase.table('inventory_item').delete().eq('id', item_id).execute()
        return '', 204
    except Exception as e:
        print(f"Error deleting inventory item: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensors', methods=['GET'])
def get_sensor_data():
    try:
        # Get latest sensor data within last 24 hours
        since_24h = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        response = supabase.table('sensor_data').select('*').gte('timestamp', since_24h).order('timestamp', desc=True).limit(1).execute()
        
        if response.data:
            return jsonify(format_sensor(response.data[0]))
        return jsonify({})
    except Exception as e:
        print(f"Error fetching sensor data: {e}")
        return jsonify({})

@app.route('/api/sensors', methods=['POST'])
def add_sensor_data():
    try:
        data = request.get_json()
        
        sensor_data = {
            'co2_ppm': data.get('co2_ppm'),
            'ammonia_ppm': data.get('ammonia_ppm'),
            'h2s_ppm': data.get('h2s_ppm'),
            'door_open': data.get('door_open', False),
            'air_quality': data.get('air_quality', 'unknown')
        }
        
        response = supabase.table('sensor_data').insert(sensor_data).execute()
        
        if response.data:
            return jsonify(format_sensor(response.data[0])), 201
        else:
            return jsonify({'error': 'Failed to create sensor data'}), 500
            
    except Exception as e:
        print(f"Error adding sensor data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensors/history')
def get_sensor_history():
    try:
        hours = request.args.get('hours', 24, type=int)
        since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        
        response = supabase.table('sensor_data').select('*').gte('timestamp', since).order('timestamp', desc=False).execute()
        
        sensors = [format_sensor(sensor) for sensor in response.data]
        return jsonify(sensors)
    except Exception as e:
        print(f"Error fetching sensor history: {e}")
        return jsonify([])

@app.route('/api/check_spoilage')
def check_spoilage():
    """Check for potential spoilage based on sensor data and item age"""
    try:
        # Get latest sensor data within last 24 hours
        since_24h = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        sensor_response = supabase.table('sensor_data').select('*').gte('timestamp', since_24h).order('timestamp', desc=True).limit(1).execute()
        latest_sensor = sensor_response.data[0] if sensor_response.data else None
        
        # Get all non-spoiled items
        items_response = supabase.table('inventory_item').select('*').eq('is_spoiled', False).execute()
        items = items_response.data
        
        spoiled_items = []
        warnings = []
        
        if latest_sensor:
            # Check ammonia levels
            if latest_sensor.get('ammonia_ppm') and latest_sensor['ammonia_ppm'] > 25:
                for item in items:
                    if item['category'] in ['meat', 'dairy', 'seafood']:
                        supabase.table('inventory_item').update({'is_spoiled': True}).eq('id', item['id']).execute()
                        spoiled_items.append(item['name'])
                warnings.append(f"High ammonia detected: {latest_sensor['ammonia_ppm']:.2f} PPM")
            
            # Check H2S levels
            if latest_sensor.get('h2s_ppm') and latest_sensor['h2s_ppm'] > 10:
                for item in items:
                    if item['category'] in ['meat', 'dairy', 'seafood']:
                        supabase.table('inventory_item').update({'is_spoiled': True}).eq('id', item['id']).execute()
                        spoiled_items.append(item['name'])
                warnings.append(f"High H2S detected: {latest_sensor['h2s_ppm']:.2f} PPM")
            
            # Check air quality
            if latest_sensor.get('air_quality') == 'poor':
                warnings.append("Poor air quality detected - possible spoiled food")
            
            # Check CO2 levels
            if latest_sensor.get('co2_ppm') and latest_sensor['co2_ppm'] > 1000:
                warnings.append(f"High CO2 detected: {latest_sensor['co2_ppm']} PPM - check ventilation")
            
            # Check if door is open
            if latest_sensor.get('door_open'):
                warnings.append("Door is open")
        
        # Check expiry dates
        for item in items:
            if item.get('expiry_date'):
                expiry_date = datetime.fromisoformat(item['expiry_date'].replace('Z', '+00:00'))
                days_since_expiry = (datetime.utcnow() - expiry_date.replace(tzinfo=None)).days
                if days_since_expiry > 0:
                    supabase.table('inventory_item').update({'is_spoiled': True}).eq('id', item['id']).execute()
                    spoiled_items.append(item['name'])
        
        return jsonify({
            'spoiled_items': list(set(spoiled_items)),
            'warnings': warnings,
            'air_quality': latest_sensor['air_quality'] if latest_sensor else 'unknown',
            'door_open': latest_sensor['door_open'] if latest_sensor else False,
            'ammonia_level': latest_sensor['ammonia_ppm'] if latest_sensor else None,
            'h2s_level': latest_sensor['h2s_ppm'] if latest_sensor else None,
            'co2_level': latest_sensor['co2_ppm'] if latest_sensor else None
        })
        
    except Exception as e:
        print(f"Error checking spoilage: {e}")
        return jsonify({
            'spoiled_items': [],
            'warnings': ['Error checking spoilage'],
            'air_quality': 'unknown',
            'door_open': False,
            'ammonia_level': None,
            'h2s_level': None,
            'co2_level': None
        })

if __name__ == '__main__':
    # Run on all interfaces so it's accessible from other devices
    app.run(host='0.0.0.0', port=5000, debug=True)
