from flask import Blueprint, render_template, request, current_app
from datetime import datetime
from database import db

gallery_bp = Blueprint('gallery', __name__)

class GalleryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=True, info={'migrate': True})  # Kept for backward compatibility
    youtube_url = db.Column(db.String(500), nullable=True, info={'migrate': True})  # Kept for backward compatibility
    media_url = db.Column(db.String(500), nullable=True)
    media_type = db.Column(db.String(20), nullable=True)  # 'image' or 'youtube'
    caption = db.Column(db.String(200), nullable=False, default='', server_default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, media_url=None, media_type=None, caption=None, **kwargs):
        # Process media fields before initialization
        media_type = (media_type or '').lower().strip()
        media_url = (media_url or '').strip()
        
        # Explicitly handle caption
        self.caption = caption.strip() if caption else ''
        
        # Validate and normalize media type
        if media_url:
            # If media_type was explicitly set, use that
            if media_type in ['image', 'youtube']:
                pass
            else:
                # Auto-detect type from URL if not specified
                if any(x in media_url for x in ['youtube.com', 'youtu.be']):
                    media_type = 'youtube'
                elif any(ext in media_url.lower().split('?')[0] for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    media_type = 'image'
                else:
                    raise ValueError("Invalid media URL - must be a valid image or YouTube URL")
            
            # Set all relevant fields
            kwargs['media_url'] = media_url
            kwargs['media_type'] = media_type
            if media_type == 'image':
                kwargs['image_url'] = media_url
                kwargs['youtube_url'] = None
            else:
                kwargs['youtube_url'] = media_url
                kwargs['image_url'] = None
        
        super(GalleryItem, self).__init__(**kwargs)

def fix_misclassified_items():
    """Fix incorrectly classified gallery items"""
    with current_app.app_context():
        with db.engine.begin() as conn:
            # Fix videos
            video_count = conn.execute(db.text("""
            UPDATE gallery_item 
            SET media_type = 'youtube', image_url = NULL 
            WHERE youtube_url IS NOT NULL AND 
                  (media_type IS NULL OR media_type != 'youtube')
        """)).rowcount
        
            # Fix images
            image_count = conn.execute(db.text("""
            UPDATE gallery_item 
            SET media_type = 'image', youtube_url = NULL 
            WHERE image_url IS NOT NULL AND 
                  (media_type IS NULL OR media_type != 'image')
        """)).rowcount
    
    return {'videos_fixed': video_count, 'images_fixed': image_count}

@gallery_bp.route('/fix-classification', methods=['GET', 'POST'])
def fix_classification():
    """Route to fix misclassified items"""
    try:
        result = fix_misclassified_items()
        return {
            'status': 'success',
            'fixed_items': result,
            'message': f"Fixed {result['videos_fixed']} videos and {result['images_fixed']} images"
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }, 500

@gallery_bp.route('/', strict_slashes=False)
def gallery():
    media_filter = request.args.get('filter', 'all')
    
    query = GalleryItem.query
    
    if media_filter == 'images':
        query = query.filter(
            (GalleryItem.media_type == 'image') &
            (GalleryItem.image_url.isnot(None))
        )
    elif media_filter == 'videos':
        query = query.filter(
            (GalleryItem.media_type == 'youtube') &
            (GalleryItem.youtube_url.isnot(None))
        )
    
    items = query.order_by(GalleryItem.created_at.desc()).all()
    
    # Ensure media_url is not None before passing to template
    for item in items:
        if item.media_url is None:
            item.media_url = item.image_url or item.youtube_url or ''
    
    return render_template('gallery.html', 
                         gallery_items=items,
                         current_filter=media_filter)

__all__ = ['gallery_bp', 'GalleryItem', 'db']
