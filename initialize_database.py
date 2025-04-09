from main import app, db
import sys

print("Initializing database connection...")
with app.app_context():
    try:
        print("Creating database tables...")
        db.create_all()
        print("Successfully created database tables")
    except Exception as e:
        print(f"Error initializing database: {str(e)}", file=sys.stderr)
        sys.exit(1)
