import os
os.environ['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ticket_user:simplepass123@localhost:5432/ticket_db?sslmode=disable'

from main import app, db
from sqlalchemy import inspect

print("Testing database connection...")
with app.app_context():
    try:
        db.engine.connect()
        print("✅ Connection successful!")
        
        inspector = inspect(db.engine)
        print("Existing tables:", inspector.get_table_names())
    except Exception as e:
        print(f"❌ Connection failed: {e}")
