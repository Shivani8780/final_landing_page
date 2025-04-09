from main import app, db
from sqlalchemy import inspect

with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # Check what tables exist
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("Existing tables:", tables)
    
    # Specifically check for ticket_order table
    if 'ticket_order' in tables:
        print("SUCCESS: ticket_order table exists!")
    else:
        print("ERROR: ticket_order table was not created")
