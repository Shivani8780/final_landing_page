from main import app, db
from sqlalchemy import inspect

print("\n=== Database Configuration ===")
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"Environment: {'Production' if 'railway' in str(app.config['SQLALCHEMY_DATABASE_URI']).lower() else 'Development'}")

with app.app_context():
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("\n=== Database Tables ===")
        print("Existing tables:", tables)
        
        if 'ticket_order' in tables:
            print("\n=== Table Structure ===")
            print("ticket_order columns:")
            for column in inspector.get_columns('ticket_order'):
                print(f"- {column['name']}: {column['type']}")
        else:
            print("\nERROR: ticket_order table missing!")
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
