from main import app, db
from sqlalchemy import text

def init_db():
    with app.app_context():
        # Verify connection
        try:
            result = db.session.execute(text('SELECT 1')).scalar()
            print('✅ Database connection successful:', result == 1)
            
            # Recreate tables
            db.drop_all()
            db.create_all()
            print('✅ Tables recreated')
            
            # Verify tables
            tables = [t.name for t in db.metadata.sorted_tables]
            print('✅ Existing tables:', tables)
            
        except Exception as e:
            print('❌ Error:', str(e))

if __name__ == '__main__':
    init_db()
