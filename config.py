import os

class Config:
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://ticket_user:simplepass123@localhost:5432/ticket_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
