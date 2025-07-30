#User model
from app.extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    business_name = db.Column(db.String(120))
    business_type = db.Column(db.String(120))
    business_description = db.Column(db.Text)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(30))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    province = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    maps_link = db.Column(db.String(300))
    location = db.Column(db.String(200))