-- Supabase Schema for Fridge Inventory System
-- Drop existing tables if they exist
DROP TABLE IF EXISTS sensor_data CASCADE;
DROP TABLE IF EXISTS inventory_item CASCADE;

-- Create inventory_item table
CREATE TABLE inventory_item (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    unit VARCHAR(20) NOT NULL,
    added_date TIMESTAMPTZ DEFAULT NOW(),
    expiry_date TIMESTAMPTZ,
    category VARCHAR(50),
    notes TEXT,
    is_spoiled BOOLEAN DEFAULT FALSE,
    qr_code TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create sensor_data table
CREATE TABLE sensor_data (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    co2_ppm FLOAT,
    ammonia_ppm FLOAT,
    h2s_ppm FLOAT,
    door_open BOOLEAN,
    air_quality VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for inventory_item
CREATE TRIGGER update_inventory_item_updated_at
    BEFORE UPDATE ON inventory_item
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE inventory_item ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensor_data ENABLE ROW LEVEL SECURITY;

-- Create policies for inventory_item
-- Allow all operations for anonymous users (you can restrict this later)
CREATE POLICY "Allow all for inventory_item" ON inventory_item
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Create policies for sensor_data
-- Allow all operations for anonymous users
CREATE POLICY "Allow all for sensor_data" ON sensor_data
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Create indexes for better performance
CREATE INDEX idx_inventory_item_category ON inventory_item(category);
CREATE INDEX idx_inventory_item_expiry_date ON inventory_item(expiry_date);
CREATE INDEX idx_inventory_item_is_spoiled ON inventory_item(is_spoiled);
CREATE INDEX idx_sensor_data_timestamp ON sensor_data(timestamp DESC);

-- Insert sample data (optional)
INSERT INTO inventory_item (name, quantity, unit, category, expiry_date, notes) VALUES
    ('Chicken Breast', 2, 'kg', 'meat', NOW() + INTERVAL '7 days', 'Fresh from market'),
    ('Milk', 1, 'liters', 'dairy', NOW() + INTERVAL '5 days', 'Organic whole milk'),
    ('Carrots', 500, 'g', 'vegetables', NOW() + INTERVAL '14 days', 'Baby carrots'),
    ('Ice Cream', 1, 'liters', 'frozen', NOW() + INTERVAL '90 days', 'Vanilla flavor');

-- Insert sample sensor data
INSERT INTO sensor_data (co2_ppm, ammonia_ppm, h2s_ppm, door_open, air_quality) VALUES
    (450, 5, 2, false, 'good');

-- Grant permissions (for public schema)
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

