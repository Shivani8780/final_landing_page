from flask import Flask
from db_config import db, init_db
from admin_interface import create_admin_blueprint
import register_blueprints
import os

def create_app():
    app = Flask(__name__)
    
    # Initialize configurations
    init_db(app)
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
    
    # Register blueprints
    admin_bp = create_admin_blueprint(app.config['UPLOAD_FOLDER'])
    app.register_blueprint(admin_bp)
    register_blueprints.register_blueprints()
    
    return app

def initialize_app():
    app = create_app()
    with app.app_context():
        db.create_all()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    return app

if __name__ == '__main__':
    app = initialize_app()
    app.run(host='0.0.0.0', port=8080)
