from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session, jsonify
import io
import xlsxwriter
from flask_restful import Api, Resource, reqparse
from config import get_config
from flask_sqlalchemy import SQLAlchemy
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
app.config.from_object(get_config())
app.jinja_env.globals.update(get_event_name=get_event_name)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)
CORS(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

# Your TicketOrder model
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

# [Include all your other existing routes here]

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
