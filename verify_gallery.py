from main import app, db

with app.app_context():
    exists = db.engine.has_table('gallery_item')
    print(f"GalleryItem table exists: {exists}")
    
    if exists:
        count = db.session.execute('SELECT COUNT(*) FROM gallery_item').scalar()
        print(f"Number of gallery items: {count}")
