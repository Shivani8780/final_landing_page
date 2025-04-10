from main import app
from flask_migrate import Migrate

def run_migrations():
    with app.app_context():
        try:
            from flask_migrate import upgrade
            upgrade()
            print("✅ Migrations applied successfully")
            return True
        except Exception as e:
            print("❌ Migration error:", str(e))
            return False

if __name__ == "__main__":
    run_migrations()
