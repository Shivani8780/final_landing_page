from flask import Flask
from db_config import db, init_db
import register_blueprints
from gallery_module import GalleryItem

def create_app():
    app = Flask(__name__)
    init_db(app)
    register_blueprints.register_blueprints()
    return app

def init_database():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database tables created")

if __name__ == '__main__':
    app = create_app()
    init_database()
    app.run(host='0.0.0.0', port=8080)
