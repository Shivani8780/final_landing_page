from main import app
from db_config import db
from gallery_module import GalleryItem

with app.app_context():
    items = GalleryItem.query.all()
    for item in items:
        print(f"ID: {item.id}")
        print(f"Media URL: {item.media_url}")
        print(f"Media Type: {item.media_type}")
        print(f"Image URL: {item.image_url}")
        print(f"Youtube URL: {item.youtube_url}")
        print("------")
