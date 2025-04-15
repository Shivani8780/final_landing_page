import sys
import os

# Add the project root directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, db, GalleryItem

def update_video_availability():
    with app.app_context():
        videos = GalleryItem.query.filter_by(media_type='youtube').all()
        for video in videos:
            if video.is_available is None or video.is_available is False:
                video.is_available = True
                print(f"Updating video ID {video.id} to is_available=True")
        db.session.commit()
        print("All video availability updated successfully.")

if __name__ == "__main__":
    update_video_availability()
