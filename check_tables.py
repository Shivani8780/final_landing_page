from main import app, db

def check_tables():
    with app.app_context():
        try:
            tables = [t.name for t in db.metadata.sorted_tables]
            print("Current tables:", tables)
            return True
        except Exception as e:
            print("Error checking tables:", str(e))
            return False

if __name__ == "__main__":
    check_tables()
