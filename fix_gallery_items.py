from main import db
from gallery_module import GalleryItem

def fix_misclassified_items():
    # Fix items with youtube_url but wrong media_type
    videos = GalleryItem.query.filter(
        (GalleryItem.youtube_url.isnot(None)) &
        (GalleryItem.media_type != 'youtube')
    ).all()
    
    for item in videos:
        item.media_type = 'youtube'
        item.image_url = None
        
    # Fix items with image_url but wrong media_type    
    images = GalleryItem.query.filter(
        (GalleryItem.image_url.isnot(None)) &
        (GalleryItem.media_type != 'image')
    ).all()
    
    for item in images:
        item.media_type = 'image'
        item.youtube_url = None
        
    db.session.commit()
    print(f"Fixed {len(videos)} videos and {len(images)} images")

if __name__ == '__main__':
    fix_misclassified_items()
