import os
os.environ['RAILWAY_ENVIRONMENT'] = '1'  # Force production mode
os.environ['DATABASE_URL'] = 'postgresql://postgres:JrHLCmATDSNBeQwNEterClFRUhWxUnKD@trolley.proxy.rlwy.net:13877/railway'

from main import app, db

print("Initializing Railway production database...")
print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
