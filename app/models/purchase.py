from app.extensions import db
from datetime import datetime

class CouponPurchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    coupon_id = db.Column(db.Integer, nullable=False)
    secret_code = db.Column(db.String(4), nullable=False)
    redeemed = db.Column(db.Boolean, default=False)
    redeemed_at = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
