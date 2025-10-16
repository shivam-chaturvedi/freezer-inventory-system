@echo off
echo ========================================
echo Fridge Inventory System Setup (Windows)
echo ========================================
echo.

echo Installing Python dependencies...
pip install -r requirements-windows.txt

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Go to Supabase dashboard and run schema.sql
echo 2. Create .env file with your Supabase credentials
echo 3. Run: python app.py
echo 4. Open: http://localhost:5000
echo.
echo For detailed instructions, see SUPABASE_SETUP.md
echo.
pause

