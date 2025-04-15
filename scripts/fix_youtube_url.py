import sys
import os

# Add the project root directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, db
from gallery_module import GalleryItem

def fix_youtube_url():
    with app.app_context():
        videos = GalleryItem.query.filter_by(media_type='youtube').all()
        for video in videos:
            if not video.youtube_url and video.media_url:
                video.youtube_url = video.media_url
                print(f"Updated youtube_url for video ID {video.id}")
        db.session.commit()
        print("youtube_url fields updated successfully.")

if __name__ == "__main__":
    fix_youtube_url()
