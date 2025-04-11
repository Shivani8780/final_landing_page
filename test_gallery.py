from main import app, db
from gallery_module import GalleryItem

def inspect_gallery():
    with app.app_context():
        print("Current Gallery Items:")
        print("----------------------")
        items = GalleryItem.query.all()
        for item in items:
            print(f"ID: {item.id}")
            print(f"Media URL: {item.media_url}")
            print(f"Media Type: {item.media_type}")
            print(f"Image URL: {item.image_url}")
            print(f"Youtube URL: {item.youtube_url}")
            print("------")

if __name__ == '__main__':
    inspect_gallery()
