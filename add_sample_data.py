from start_app import create_app
from gallery_module import GalleryItem
from main import db

app = create_app()

def add_samples():
    with app.app_context():
        # Single sample
        db.session.add(GalleryItem(
            media_url='https://example.com/image.jpg',
            media_type='image',
            caption='Sample Image'
        ))
        
        # Multiple samples
        samples = [
            {'media_url': '/static/event1.jpg', 'media_type': 'image', 'caption': 'Event Photo'},
            {'media_url': 'https://youtube.com/watch?v=EXAMPLE', 'media_type': 'youtube', 'caption': 'Event Video'}
        ]
        
        for item in samples:
            db.session.add(GalleryItem(**item))
            
        db.session.commit()
        print("Added sample gallery items")

if __name__ == '__main__':
    add_samples()
