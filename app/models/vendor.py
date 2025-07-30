#backend/app/models/vendor.py
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(150), nullable=False)
    business_type = db.Column(db.String(120))
    business_description = db.Column(db.Text)
    contact_person = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    street_address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    province = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    google_maps_link = db.Column(db.String(255))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
