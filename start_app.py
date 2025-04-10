from main import app, db
import register_blueprints

# Initialize the app
def create_app():
    register_blueprints.register_blueprints()
    return app

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
