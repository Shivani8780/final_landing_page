from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session, jsonify
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

app = Flask(__name__)
app.config.from_object(get_config())

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

# [Include all your other existing routes here]

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
