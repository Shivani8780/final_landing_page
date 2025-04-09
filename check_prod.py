import os
os.environ['RAILWAY_ENVIRONMENT'] = '1'  # Force production mode
os.environ['DATABASE_URL'] = 'postgresql://postgres:JrHLCmATDSNBeQwNEterClFRUhWxUnKD@trolley.proxy.rlwy.net:13877/railway'

from main import app, db
from sqlalchemy import inspect

print("\n=== PRODUCTION DATABASE VERIFICATION ===")
print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("\nTables in production:", tables)
        
        if 'ticket_order' in tables:
            print("\nTable structure:")
            for col in inspector.get_columns('ticket_order'):
                print(f"- {col['name']}: {col['type']}")
        else:
            print("\nERROR: ticket_order table missing in production!")
    except Exception as e:
        print(f"\nPRODUCTION ERROR: {str(e)}")
