from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session,jsonify
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, validators
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd
import json
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-development-key-here')

# Render production configuration
if 'RENDER' in os.environ:
    # On Render - use their PostgreSQL
    db_url = os.environ['DATABASE_URL']
else:
    # Local development
    db_url = os.getenv('DATABASE_URL', 'postgresql://ticket_user:simplepass123@localhost:5432/ticket_db')

# Convert postgres:// to postgresql:// if needed
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
if db_url:
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    print(f"Using database URL: {db_url}")  # For debugging
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)
CORS(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

# Define a parser for request data
def validate_event(event):
    valid_events = ['winter-festival', 'spring-jazz', 'summer-rock']
    if event not in valid_events:
        raise ValueError(f"Invalid event: {event}. Must be one of {valid_events}.")
    return event

order_parser = reqparse.RequestParser()
order_parser.add_argument('name', type=str, required=True, help='Name cannot be blank')
order_parser.add_argument('email', type=str, required=True, help='Email cannot be blank')
order_parser.add_argument('quantity', type=int, required=True, help='Quantity cannot be blank')
order_parser.add_argument('event', type=validate_event, required=True, help='Event cannot be blank')

class TicketOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

    def delete(self, order_id):
        order = TicketOrder.query.get(order_id)
        if not order:
            return {'message': 'Order not found'}, 404
        db.session.delete(order)
        db.session.commit()
        return {'message': 'Order deleted successfully'}

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

    def post(self):
        try:
            args = order_parser.parse_args()
            amount = args['quantity'] * 500  # Calculate amount
            order = TicketOrder(
                name=args['name'],
                email=args['email'],
                quantity=args['quantity'],
                event=args['event'],
                amount=amount
            )
            db.session.add(order)
            db.session.commit()
            return {'message': 'Order created', 'order_id': order.id}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'message': 'An error occurred while creating the order', 'error': str(e)}, 500

# Add resources to the API
api.add_resource(TicketOrderListResource, '/api/orders')
api.add_resource(TicketOrderResource, '/api/orders/<int:order_id>')


class TicketForm(FlaskForm):
    name = StringField('Full Name', [validators.InputRequired()])
    email = StringField('Email', [validators.InputRequired(), validators.Email()])
    quantity = IntegerField('Quantity', [validators.InputRequired(), validators.NumberRange(min=1, max=10)])
    event = SelectField('Event', choices=[
        ('winter-festival', 'Winter Music Festival 2025'), 
        ('spring-jazz', 'Spring Jazz Night 2025'),
        ('summer-rock', 'Summer Rock Fest 2025')
    ])

def check_auth(username, password):
    """Check if a username/password combination is valid."""
    return username == 'admin' and password == 'Shiva'  # Replace with secure method

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# Load event data
def load_events():
    with open('data/events.json') as f:
        return json.load(f)

@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

@app.route('/')
def home():
    event_date = datetime(2025, 12, 25, 19, 30)  # Updated to 2025
    return render_template('index.html', event_date=event_date.isoformat())

@app.route('/history')
def history():
    events = load_events()
    return render_template('history.html', events=events)

@app.route('/tickets', methods=['GET', 'POST'])
def tickets():
    if request.method == 'POST':
        # Process form data
        name = request.form.get('name')
        email = request.form.get('email')
        quantity = int(request.form.get('quantity'))
        event = request.form.get('event')
        
        # Calculate amount (example: ₹500 per ticket)
        amount = quantity * 500  # Amount in INR
        
        # Create a new order in the database
        order = TicketOrder(name=name, email=email, quantity=quantity, event=event, amount=amount)
        db.session.add(order)
        db.session.commit()
        
        # Redirect to WhatsApp
        return redirect(url_for('whatsapp_redirect', order_id=order.id))
    
    return render_template('tickets.html')

@app.route('/whatsapp_redirect', methods=['GET'])
def whatsapp_redirect():
    order_id = request.args.get('order_id')
    order = TicketOrder.query.get(order_id)
    
    if order:
        # Construct WhatsApp URL with pre-filled message
        whatsapp_number = "6352641421"  # Replace with seller's WhatsApp number
        message = f"Hello, I would like to purchase {order.quantity} tickets for {get_event_name(order.event)}. My name is {order.name}. The total amount is ₹{order.amount}."
        whatsapp_url = f"https://wa.me/{whatsapp_number}?text={message}"
        return redirect(whatsapp_url)
    
    flash('Order not found', 'error')
    return redirect(url_for('tickets'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if check_auth(username, password):
            session['logged_in'] = True
            return redirect(url_for('export_data'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('admin_login.html')

@app.route('/admin/orders')
@requires_auth
def admin_orders():
    orders = TicketOrder.query.all()
    return render_template('admin_orders.html', orders=orders,get_event_name=get_event_name)

@app.route('/admin/delete/<int:order_id>', methods=['POST'])
@requires_auth
def delete_order(order_id):
    order = TicketOrder.query.get(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        flash('Order deleted successfully', 'success')
    else:
        flash('Order not found', 'error')
    return redirect(url_for('admin_orders'))

@app.route('/admin/update/<int:order_id>', methods=['GET', 'POST'])
@requires_auth
def update_order(order_id):
    order = TicketOrder.query.get(order_id)
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('admin_orders'))

    if request.method == 'POST':
        order.name = request.form.get('name')
        order.email = request.form.get('email')
        order.quantity = int(request.form.get('quantity'))
        order.event = request.form.get('event')
        order.amount = order.quantity * 500  # Update amount based on quantity
        db.session.commit()
        flash('Order updated successfully', 'success')
        return redirect(url_for('admin_orders'))

    return render_template('update_order.html', order=order)

@app.route('/export')
@requires_auth
def export_data():
    # Query all ticket orders
    orders = TicketOrder.query.all()
    
    # Convert to a list of dictionaries
    data = [{
        "Name": order.name,
        "Email": order.email,
        "Event": get_event_name(order.event),
        "Quantity": order.quantity,
        "Amount": order.amount,
        "Created At": order.created_at
    } for order in orders]
    
    # Create a DataFrame
    df = pd.DataFrame(data)
    
    # Save to Excel
    file_path = 'ticket_orders.xlsx'
    df.to_excel(file_path, index=False)
    
    # Send the file to the user
    return send_file(file_path, as_attachment=True)


def get_event_name(event_id):
    names = {
        'winter-festival': 'Winter Music Festival 2025',
        'spring-jazz': 'Spring Jazz Night 2025',
        'summer-rock': 'Summer Rock Fest 2025'
    }
    return names.get(event_id, 'Winter Music Festival 2025')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created before running the app
    app.run(debug=True)