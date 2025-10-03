#!/usr/bin/env python3
"""
Database migration script to fix schema issues
"""

import sqlite3
import os
from datetime import datetime

def fix_database():
    """Fix the database schema by recreating it with the new structure"""
    
    db_path = 'freezer_inventory.db'
    
    # Backup the old database
    if os.path.exists(db_path):
        backup_path = f'freezer_inventory_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        os.rename(db_path, backup_path)
        print(f"Backed up old database to: {backup_path}")
    
    # Create new database with correct schema
    from app import app, db
    
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables with new schema
        db.create_all()
        
        print("Database schema updated successfully!")
        print("New database created with correct sensor columns.")

if __name__ == "__main__":
    fix_database()
