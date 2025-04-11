from flask import Blueprint, request, jsonify
from gallery_module import GalleryItem
from db_config import db
from werkzeug.utils import secure_filename
import os

def create_admin_blueprint(upload_folder='static/uploads'):
    admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}
    os.makedirs(upload_folder, exist_ok=True)

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @admin_bp.route('/gallery', methods=['POST'])
    def add_gallery_item():
        data = request.form
        media_type = data.get('media_type')
        media_url = data.get('media_url')
        caption = data.get('caption', '')
        
        if not media_type or not media_url:
            return jsonify({'error': 'Both media type and URL are required'}), 400
            
        if media_type not in ['image', 'youtube']:
            return jsonify({'error': 'Invalid media type'}), 400
            
        if media_type == 'youtube':
            if not media_url.startswith('https://youtu.be/'):
                return jsonify({'error': 'YouTube URLs must start with https://youtu.be/'}), 400
            # Normalize YouTube URL
            media_url = media_url.split('?')[0]  # Remove any query parameters
            kwargs['media_url'] = media_url
            
        try:
            # Create new gallery item
            new_item = GalleryItem(
                media_url=media_url,
                media_type=media_type,
                caption=caption,
                image_url=media_url if media_type == 'image' else None,
                youtube_url=media_url if media_type == 'youtube' else None
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            return jsonify({
                'message': 'Upload successful',
                'data': {
                    'id': new_item.id,
                    'url': new_item.media_url,
                    'type': new_item.media_type,
                    'caption': new_item.caption
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to add gallery item: {str(e)}'}), 500
        
    return admin_bp
