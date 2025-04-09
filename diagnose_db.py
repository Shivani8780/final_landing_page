from main import app, db
import sqlalchemy as sa
from sqlalchemy import inspect

def check_database():
    with app.app_context():
        try:
            # 1. Print database connection info
            print(f"\nDatabase URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # 2. Test raw connection
            with db.engine.connect() as conn:
                print("Connection successful!")
                
                # 3. List all tables
                result = conn.execute(sa.text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = current_schema()"
                ))
                tables = [row[0] for row in result]
                print(f"Tables in current schema: {tables}")
                
                # 4. Check ticket_order specifically
                if 'ticket_order' in tables:
                    print("\nTicket_order table exists! Checking structure...")
                    inspector = inspect(db.engine)
                    columns = inspector.get_columns('ticket_order')
                    print("Columns:", [c['name'] for c in columns])
                else:
                    print("\nERROR: ticket_order table missing!")
                    
        except Exception as e:
            print(f"\nDatabase error: {str(e)}")

if __name__ == '__main__':
    check_database()
