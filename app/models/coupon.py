# backend/app/models/coupon.py

from app.extensions import db
from datetime import datetime
import uuid
import random

class Coupon(db.Model):
    __tablename__ = 'coupon'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    
    # NEW FIELD: Public coupon ID shown to both client and vendor
    coupon_id = db.Column(db.String(20), unique=True, default=lambda: f"CUP{random.randint(10000, 99999)}")
    # NEW FIELD: Vendor reference (foreign key setup optional for now)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id", name="fk_coupon_vendor_id"))
    
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=False)
    discount_type = db.Column(db.String(50), nullable=False)
    discount_value = db.Column(db.String(50), nullable=False)
    minimum_purchase = db.Column(db.String(50), nullable=True)
    terms_and_conditions = db.Column(db.Text, nullable=True)
    activation_date = db.Column(db.String(50), nullable=True)
    expiration_date = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    vendor = db.relationship("Vendor", backref="coupons", lazy=True)

    # NEW FIELD: Coupon status
    status = db.Column(db.String(20), default='active')  # active, purchased, redeemed

    # NEW FIELD: Secret 4-digit code after purchase (only client sees this)
    redemption_code = db.Column(db.String(10), nullable=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    purchased = db.Column(db.Integer, default=0)
    redeemed = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100), nullable=True)  # City, Area, or Vendor Location


