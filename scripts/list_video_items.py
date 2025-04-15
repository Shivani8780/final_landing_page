import sys
import os

# Add the project root directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, db
from gallery_module import GalleryItem

def list_video_items():
    with app.app_context():
        videos = GalleryItem.query.filter_by(media_type='youtube').all()
        for video in videos:
            print(f"ID: {video.id}, youtube_url: {video.youtube_url}, is_available: {video.is_available}")

if __name__ == "__main__":
    list_video_items()
