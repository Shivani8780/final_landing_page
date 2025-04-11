from main import app, db
from gallery_module import GalleryItem

# Temporarily remove bind key
GalleryItem.__bind_key__ = None

with app.app_context():
    try:
        # List all gallery items
        items = GalleryItem.query.all()
        print(f"Found {len(items)} gallery items:")
        for item in items:
            print(f"\nID: {item.id}")
            print(f"Media URL: {item.media_url}")
            print(f"Media Type: {item.media_type}")
            print(f"Image URL: {item.image_url}")
            print(f"YouTube URL: {item.youtube_url}")
            
            # Fix media_type if missing
            if not item.media_type:
                new_type = 'youtube' if 'youtu.be' in (item.media_url or '') else 'image'
                item.media_type = new_type
                db.session.commit()
                print(f"Fixed item {item.id}: Set type to {new_type}")
                
    except Exception as e:
        print(f"Error: {str(e)}")
