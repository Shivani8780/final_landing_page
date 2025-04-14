from flask import Blueprint, request, render_template
from gallery_module import GalleryItem  # Correct import from gallery_module

bp = Blueprint('gallery_enhanced', __name__)

@bp.route('/gallery-enhanced')
def gallery_enhanced():
    filter_type = request.args.get('filter', 'all')
    gallery_items = GalleryItem.query.all()
    return render_template('gallery_enhanced.html',
                         gallery_items=gallery_items,
                         current_filter=filter_type)
