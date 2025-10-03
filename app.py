from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///freezer_inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # pieces, kg, liters, etc.
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    category = db.Column(db.String(50))  # meat, vegetables, dairy, etc.
    notes = db.Column(db.Text)
    is_spoiled = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            'added_date': self.added_date.isoformat(),
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'category': self.category,
            'notes': self.notes,
            'is_spoiled': self.is_spoiled
        }

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    temperature = db.Column(db.Float)  # in Celsius
    humidity = db.Column(db.Float)     # in percentage
    door_open = db.Column(db.Boolean)  # True if door is open
    light_level = db.Column(db.Float)  # Optional light sensor
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'temperature': self.temperature,
            'humidity': self.humidity,
            'door_open': self.door_open,
            'light_level': self.light_level
        }

# Routes
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/touch')
def touch_interface():
    return render_template('touch_interface.html')

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    items = InventoryItem.query.all()
    return jsonify([item.to_dict() for item in items])

@app.route('/api/inventory', methods=['POST'])
def add_inventory_item():
    data = request.get_json()
    
    item = InventoryItem(
        name=data['name'],
        quantity=data['quantity'],
        unit=data['unit'],
        category=data.get('category', ''),
        notes=data.get('notes', ''),
        expiry_date=datetime.fromisoformat(data['expiry_date']) if data.get('expiry_date') else None
    )
    
    db.session.add(item)
    db.session.commit()
    
    return jsonify(item.to_dict()), 201

@app.route('/api/inventory/<int:item_id>', methods=['PUT'])
def update_inventory_item(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    data = request.get_json()
    
    item.name = data.get('name', item.name)
    item.quantity = data.get('quantity', item.quantity)
    item.unit = data.get('unit', item.unit)
    item.category = data.get('category', item.category)
    item.notes = data.get('notes', item.notes)
    item.is_spoiled = data.get('is_spoiled', item.is_spoiled)
    
    if data.get('expiry_date'):
        item.expiry_date = datetime.fromisoformat(data['expiry_date'])
    
    db.session.commit()
    return jsonify(item.to_dict())

@app.route('/api/inventory/<int:item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return '', 204

@app.route('/api/sensors', methods=['GET'])
def get_sensor_data():
    # Get latest sensor data
    latest_data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    if latest_data:
        return jsonify(latest_data.to_dict())
    return jsonify({})

@app.route('/api/sensors', methods=['POST'])
def add_sensor_data():
    data = request.get_json()
    
    sensor_data = SensorData(
        temperature=data.get('temperature'),
        humidity=data.get('humidity'),
        door_open=data.get('door_open', False),
        light_level=data.get('light_level')
    )
    
    db.session.add(sensor_data)
    db.session.commit()
    
    return jsonify(sensor_data.to_dict()), 201

@app.route('/api/sensors/history')
def get_sensor_history():
    hours = request.args.get('hours', 24, type=int)
    since = datetime.utcnow() - timedelta(hours=hours)
    
    data = SensorData.query.filter(SensorData.timestamp >= since).order_by(SensorData.timestamp.asc()).all()
    return jsonify([item.to_dict() for item in data])

@app.route('/api/check_spoilage')
def check_spoilage():
    """Check for potential spoilage based on sensor data and item age"""
    latest_sensor = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    items = InventoryItem.query.filter_by(is_spoiled=False).all()
    
    spoiled_items = []
    
    if latest_sensor:
        # Check temperature - if too high, mark items as potentially spoiled
        if latest_sensor.temperature > 4:  # Above safe refrigeration temperature
            for item in items:
                if item.category in ['meat', 'dairy', 'seafood']:
                    item.is_spoiled = True
                    spoiled_items.append(item.name)
        
        # Check if door has been open too long
        if latest_sensor.door_open:
            # This would need more sophisticated logic in a real implementation
            pass
    
    # Check expiry dates
    for item in items:
        if item.expiry_date and item.expiry_date < datetime.utcnow():
            item.is_spoiled = True
            spoiled_items.append(item.name)
    
    db.session.commit()
    
    return jsonify({
        'spoiled_items': spoiled_items,
        'temperature_warning': latest_sensor.temperature > 4 if latest_sensor else False,
        'door_open': latest_sensor.door_open if latest_sensor else False
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Run on all interfaces so it's accessible from other devices
    app.run(host='0.0.0.0', port=5000, debug=True)

