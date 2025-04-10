import os
from config import Config

class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://')
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    
    # Rate limiting with Redis
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_DEFAULT = '200 per day, 50 per hour'
    
    # Security headers
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    TALISMAN_FORCE_HTTPS = True
    
    # Database pool
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
