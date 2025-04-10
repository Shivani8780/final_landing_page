from flask import Blueprint, render_template, request
from main import db
from datetime import datetime

gallery_bp = Blueprint('gallery', __name__)

class GalleryItem(db.Model):
    __bind_key__ = 'gallery'
    id = db.Column(db.Integer, primary_key=True)
    media_url = db.Column(db.String(500), nullable=False)
    media_type = db.Column(db.String(20), nullable=False)  # 'image' or 'youtube'
    caption = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@gallery_bp.route('/gallery')
def gallery():
    media_filter = request.args.get('filter', 'all')
    
    query = GalleryItem.query
    
    if media_filter == 'images':
        query = query.filter(GalleryItem.media_type == 'image')
    elif media_filter == 'videos':
        query = query.filter(GalleryItem.media_type == 'youtube')
    
    # Limit to 10 videos if that filter is selected
    if media_filter == 'videos':
        items = query.order_by(GalleryItem.created_at.desc()).limit(10).all()
    else:
        items = query.order_by(GalleryItem.created_at.desc()).all()
    
    return render_template('gallery.html', 
                         gallery_items=items,
                         current_filter=media_filter)
