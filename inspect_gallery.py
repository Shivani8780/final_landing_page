from main import app
from db_config import db, init_db
from gallery_module import GalleryItem

# Initialize the database connection
init_db(app)

with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # Query all gallery items
    items = GalleryItem.query.all()
    
    if not items:
        print("No gallery items found in database")
    else:
        print("Gallery Items in Database:")
        print("-------------------------")
        for item in items:
            print(f"ID: {item.id}")
            print(f"Media URL: {item.media_url}")
            print(f"Media Type: {item.media_type}")
            print(f"Image URL: {item.image_url}")
            print(f"Youtube URL: {item.youtube_url}")
            print("------")
