class ProdConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'your-production-secret-key'  # Change this to a secure key
    SQLALCHEMY_DATABASE_URI = 'sqlite:///prod_database.db'  # Change to your production database URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RATELIMIT_STORAGE_URL = 'memory://'  # Change to Redis or other storage in production if needed
    RATELIMIT_DEFAULT = ["200 per day", "50 per hour"]
