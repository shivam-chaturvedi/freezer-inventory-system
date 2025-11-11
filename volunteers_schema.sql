-- Volunteers Table Schema for Supabase
-- Run this SQL in your Supabase SQL Editor

-- Create volunteers table
CREATE TABLE IF NOT EXISTS volunteers (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create updated_at trigger function (if not exists)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for volunteers
DROP TRIGGER IF EXISTS update_volunteers_updated_at ON volunteers;
CREATE TRIGGER update_volunteers_updated_at
    BEFORE UPDATE ON volunteers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE volunteers ENABLE ROW LEVEL SECURITY;

-- Create policy for volunteers (allow all operations for anonymous users)
DROP POLICY IF EXISTS "Allow all for volunteers" ON volunteers;
CREATE POLICY "Allow all for volunteers" ON volunteers
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_volunteers_email ON volunteers(email);
CREATE INDEX IF NOT EXISTS idx_volunteers_name ON volunteers(name);

-- Insert sample data (optional - you can remove this)
INSERT INTO volunteers (name, email) VALUES
    ('Suraj Saran', 'suraj.saran@example.com'),
    ('Pawan Jain', 'pawan.jain@example.com')
ON CONFLICT (email) DO NOTHING;

-- Grant permissions
GRANT ALL ON volunteers TO anon, authenticated;
GRANT USAGE, SELECT ON SEQUENCE volunteers_id_seq TO anon, authenticated;

