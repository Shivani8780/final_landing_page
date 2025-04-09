import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://ticket_user:simplepass123@localhost:5432/ticket_db'

class ProductionConfig(Config):
    DB_URL = os.getenv('DATABASE_URL', '').replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = f"{DB_URL}?sslmode=require" if DB_URL else None

def get_config():
    if os.getenv('RAILWAY_ENVIRONMENT'):
        return ProductionConfig()
    return DevelopmentConfig()
