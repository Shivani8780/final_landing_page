from main import app
from gallery_module import gallery_bp

def register_blueprints():
    app.register_blueprint(gallery_bp)
    print("Gallery blueprint registered successfully")

if __name__ == '__main__':
    register_blueprints()
