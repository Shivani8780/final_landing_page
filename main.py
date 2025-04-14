from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session, jsonify
# Import gallery components
from gallery_module import gallery_bp
from gallery_routes_enhanced_fixed import bp as gallery_enhanced_bp
import io
import xlsxwriter
from flask_restful import Api, Resource, reqparse
from config import get_config
from database import db
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, validators
from datetime import datetime
import os
import pandas as pd
import json
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError

def load_events():
    try:
        with open('data/events.json') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading events: {str(e)}")
        return []

def get_event_name(event_id):
    names = {
        'winter-festival': 'Winter Music Festival 2025',
        'spring-jazz': 'Spring Jazz Night 2025',
        'summer-rock': 'Summer Rock Fest 2025'
    }
    return names.get(event_id, 'Unknown Event')

app = Flask(__name__)

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['Cache-Control'] = 'no-store, max-age=0'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response
app.register_blueprint(gallery_bp, url_prefix='/gallery')
app.register_blueprint(gallery_enhanced_bp, url_prefix='/gallery-enhanced')

# Load configuration based on environment
env = os.getenv('FLASK_ENV', 'development')
print(f"Loading configuration for FLASK_ENV={env}")
if env == 'production':
    from prod_config import ProdConfig
    app.config.from_object(ProdConfig)
    # Explicitly set required config values
    app.config['RATELIMIT_STORAGE_URL'] = ProdConfig.RATELIMIT_STORAGE_URL
    app.config['SQLALCHEMY_DATABASE_URI'] = ProdConfig.SQLALCHEMY_DATABASE_URI
else:
    app.config.from_object(get_config())
    app.config['RATELIMIT_STORAGE_URL'] = 'memory://'

# Initialize extensions after config is loaded
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
CORS(app)

# Initialize limiter with fallback to memory
try:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://'),
        default_limits=app.config.get('RATELIMIT_DEFAULT', ["200 per day", "50 per hour"])
    )
    storage_type = type(limiter.storage).__name__
    if storage_type == 'RedisStorage':
        try:
            print(f"Rate limiter using Redis storage at: {limiter.storage.storage_url}")
        except AttributeError:
            print("Rate limiter using Redis storage (URL not accessible)")
    else:
        print(f"Rate limiter using {storage_type} storage")
except Exception as e:
    print("Failed to initialize Redis, falling back to in-memory storage:", str(e))
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri='memory://',
        default_limits=["200 per day", "50 per hour"]
    )
app.jinja_env.globals.update(get_event_name=get_event_name)

# This ensures the CLI commands work properly
def register_commands(app):
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()

class TicketOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# RESTful API Resources
class TicketOrderResource(Resource):
    def get(self, order_id):
        order = TicketOrder.query.get(order_id)
        if not order:
            return {'message': 'Order not found'}, 404
        return {
            'id': order.id,
            'name': order.name,
            'email': order.email,
            'quantity': order.quantity,
            'event': order.event,
            'amount': order.amount,
            'created_at': order.created_at.isoformat()
        }

class TicketOrderListResource(Resource):
    def get(self):
        orders = TicketOrder.query.all()
        return [{
            'id': order.id,
            'name': order.name,
            'email': order.email,
            'quantity': order.quantity,
            'event': order.event,
            'amount': order.amount,
            'created_at': order.created_at.isoformat()
        } for order in orders]

# Form Classes
class TicketForm(FlaskForm):
    name = StringField('Full Name', [validators.InputRequired()])
    email = StringField('Email', [validators.InputRequired(), validators.Email()])
    quantity = IntegerField('Quantity', [validators.InputRequired(), validators.NumberRange(min=1, max=10)])
    event = SelectField('Event', choices=[
        ('winter-festival', 'Winter Music Festival 2025'), 
        ('spring-jazz', 'Spring Jazz Night 2025'),
        ('summer-rock', 'Summer Rock Fest 2025')
    ])

# Routes
@app.route('/')
def home():
    event_date = datetime(2025, 12, 25, 19, 30)
    return render_template('index.html', event_date=event_date.isoformat())

@app.route('/whatsapp_redirect')
def whatsapp_redirect():
    order_id = request.args.get('order_id')
    order = TicketOrder.query.get(order_id)
    
    if order:
        whatsapp_number = "6352641421"  # Replace with your WhatsApp number
        message = f"Hello, I would like to purchase {order.quantity} tickets for {get_event_name(order.event)}"
        whatsapp_url = f"https://wa.me/{whatsapp_number}?text={message}"
        return redirect(whatsapp_url)
    
    flash('Order not found', 'error')
    return redirect(url_for('tickets'))

@app.route('/tickets', methods=['GET', 'POST'])
def tickets():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        quantity = int(request.form.get('quantity'))
        event = request.form.get('event')
        amount = quantity * 500
        
        order = TicketOrder(name=name, email=email, quantity=quantity, event=event, amount=amount)
        try:
            db.session.add(order)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Failed to save order. Please try again.', 'error')
            return redirect(url_for('tickets'))
        
        return redirect(url_for('whatsapp_redirect', order_id=order.id))
    
    return render_template('tickets.html')

def load_events():
    try:
        with open('data/events.json') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading events: {str(e)}")
        return []

def get_event_name(event_id):
    names = {
        'winter-festival': 'Winter Music Festival 2025',
        'spring-jazz': 'Spring Jazz Night 2025',
        'summer-rock': 'Summer Rock Fest 2025'
    }
    return names.get(event_id, 'Unknown Event')

@app.route('/history')
def history():
    events = load_events()
    return render_template('history.html', events=events)

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Replace with your actual admin credentials
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        
        flash('Invalid credentials', 'error')
    return render_template('admin_login.html')

@app.route('/admin/gallery', methods=['GET', 'POST'])
def manage_gallery():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        # Get form data from new form structure
        media_type = request.form.get('media_type', '').strip()
        media_url = request.form.get('media_url', '').strip()
        caption = request.form.get('caption', '').strip()
        
        # Validate based on media type
        if media_type == 'youtube':
            if not ('youtube.com' in media_url or 'youtu.be' in media_url):
                flash('Please enter a valid YouTube URL (should contain youtube.com or youtu.be)', 'error')
                return redirect(url_for('manage_gallery'))
        elif media_type == 'image':
            if not media_url.startswith(('http://', 'https://')):
                flash('Image URL must start with http:// or https://', 'error')
                return redirect(url_for('manage_gallery'))
            if not any(ext in media_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                flash('Note: For best results, use URLs ending with .jpg, .jpeg, .png, .gif or .webp', 'info')
        
        # Create item
        print(f"Raw caption input: '{caption}'")
        
        # Create item - model will handle caption processing
        item = GalleryItem(
            media_url=media_url,
            media_type=media_type,
            caption=caption  # Pass raw caption
        )
        # Force caption update to ensure it's processed
        if hasattr(item, '_caption'):
            item._caption = caption.strip() if caption else ''
        print(f"Item after creation - Caption: '{item.caption}'")
        
        print(f"Item being saved - Caption: '{item.caption}'")
        db.session.add(item)
        db.session.commit()
        flash('Gallery item added successfully', 'success')
        return redirect(url_for('manage_gallery'))
    
    items = GalleryItem.query.order_by(GalleryItem.created_at.desc()).all()
    return render_template('admin_gallery.html', items=items)

@app.route('/admin/gallery/<int:item_id>/delete', methods=['POST'])
def delete_gallery_item(item_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    item = GalleryItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Gallery item deleted successfully', 'success')
    return redirect(url_for('manage_gallery'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    orders = TicketOrder.query.order_by(TicketOrder.created_at.desc()).all()
    return render_template('admin_orders.html', 
                         orders=orders,
                         get_event_name=get_event_name)

@app.route('/admin/export')
def export_orders():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    orders = TicketOrder.query.order_by(TicketOrder.created_at.desc()).all()
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Write headers
    headers = ['ID', 'Name', 'Email', 'Event', 'Quantity', 'Amount', 'Date']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # Write data
    for row, order in enumerate(orders, start=1):
        worksheet.write(row, 0, order.id)
        worksheet.write(row, 1, order.name)
        worksheet.write(row, 2, order.email)
        worksheet.write(row, 3, get_event_name(order.event))
        worksheet.write(row, 4, order.quantity)
        worksheet.write(row, 5, order.amount)
        worksheet.write(row, 6, order.created_at.strftime('%Y-%m-%d %H:%M'))
    
    workbook.close()
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        download_name='orders_export.xlsx',
        as_attachment=True
    )

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

@app.route('/admin/orders/<int:order_id>/delete', methods=['POST'])
def delete_order(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    order = TicketOrder.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Order deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/orders/<int:order_id>/update', methods=['GET', 'POST'])
def update_order(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    order = TicketOrder.query.get_or_404(order_id)
    if request.method == 'POST':
        order.name = request.form.get('name', order.name)
        order.email = request.form.get('email', order.email)
        order.quantity = int(request.form.get('quantity', order.quantity))
        order.event = request.form.get('event', order.event)
        order.amount = order.quantity * 500
        
        try:
            db.session.commit()
            flash('Order updated successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating order', 'error')
    
    return render_template('update.html', order=order)

@app.route('/debug/gallery')
def debug_gallery():
    items = GalleryItem.query.all()
    output = []
    for item in items:
        output.append({
            'id': item.id,
            'media_url': item.media_url,
            'media_type': item.media_type,
            'image_url': item.image_url,
            'youtube_url': item.youtube_url
        })
    return jsonify(output)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
