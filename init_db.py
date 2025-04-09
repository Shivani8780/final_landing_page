from main import app, db
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure database
if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DATABASE_URL'):
    db_url = os.getenv('DATABASE_URL', '')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    if 'railway' in db_url.lower():
        db_url += "?sslmode=require"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ticket_user:simplepass123@localhost:5432/ticket_db'

# Initialize db with app
db.init_app(app)

print("Initializing database...")
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
