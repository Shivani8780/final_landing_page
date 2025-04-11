from main import app
from gallery_module import gallery_bp
from admin_interface import create_admin_blueprint

def register_blueprints():
    app.register_blueprint(gallery_bp)
    admin_bp = create_admin_blueprint()
    app.register_blueprint(admin_bp)
    print("Blueprints registered successfully")

if __name__ == '__main__':
    register_blueprints()
