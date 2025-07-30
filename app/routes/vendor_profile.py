# backend/app/routes/vendor_profile.py

from flask import Blueprint, request, jsonify
from firebase_admin import auth as firebase_auth
from app.models.vendor import Vendor

vendor_profile_bp = Blueprint('vendor_profile', __name__, url_prefix='/api/vendor')

def verify_firebase_token(token):
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Firebase verification failed: {e}")
        return None

@vendor_profile_bp.route('/profile', methods=['GET'])
def get_vendor_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Authorization header missing'}), 401

    try:
        id_token = auth_header.split(" ")[1]
    except IndexError:
        return jsonify({'error': 'Invalid Authorization header format'}), 401

    decoded_token = verify_firebase_token(id_token)
    if not decoded_token:
        return jsonify({'error': 'Invalid Firebase token'}), 401

    email = decoded_token.get('email')
    vendor = Vendor.query.filter_by(email=email).first()
    if not vendor:
        return jsonify({'error': 'Vendor not found'}), 404

    return jsonify({
        'businessName': vendor.business_name,
        'businessType': vendor.business_type,
        'businessDescription': vendor.business_description,
        'contactPerson': vendor.contact_person,
        'email': vendor.email,
        'phone': vendor.phone,
        'streetAddress': vendor.street_address,
        'city': vendor.city,
        'province': vendor.province,
        'postalCode': vendor.postal_code,
        'maps_link': vendor.google_maps_link,
    }), 200
