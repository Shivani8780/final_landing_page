from main import app, db
from gallery_module import GalleryItem

# Temporarily remove bind key
GalleryItem.__bind_key__ = None

with app.app_context():
    try:
        items = GalleryItem.query.all()
        print(f"Found {len(items)} gallery items")
        for item in items:
            print(f"\nID: {item.id}")
            print(f"Media URL: {item.media_url}")
            print(f"Media Type: {item.media_type}")
            print(f"Image URL: {item.image_url}")
            print(f"Youtube URL: {item.youtube_url}")
    except Exception as e:
        print(f"Error: {str(e)}")
