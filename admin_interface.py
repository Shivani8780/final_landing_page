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

    @admin_bp.route('/upload', methods=['POST'])
    def upload_media():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        media_type = 'video' if file.filename.lower().endswith(('.mp4', '.mov')) else 'image'
        caption = request.form.get('caption', '')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            new_item = GalleryItem(
                media_url=f'/{filepath}',
                media_type=media_type,
                caption=caption
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

        return jsonify({'error': 'File type not allowed'}), 400

    return admin_bp
