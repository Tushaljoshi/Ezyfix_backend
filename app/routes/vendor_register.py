#backend/app/routes/vendor_register.py
from flask import Blueprint, request, jsonify
from app.models.vendor import Vendor
from app import db

vendor_bp = Blueprint('vendor', __name__, url_prefix='/api')

@vendor_bp.route('/register-vendor', methods=['POST'])
def register_vendor():
    data = request.json

    if Vendor.query.filter((Vendor.email == data['email']) | (Vendor.username == data['username'])).first():
        return jsonify({'error': 'Vendor with this email or username already exists'}), 409

    vendor = Vendor(
        business_name=data.get('businessName'),
        business_type=data.get('businessType'),
        business_description=data.get('businessDescription'),
        contact_person=data.get('contactPerson'),
        email=data['email'],
        phone=data.get('phone'),
        street_address=data.get('streetAddress'),
        city=data.get('city'),
        province=data.get('province'),
        postal_code=data.get('postalCode'),
        google_maps_link=data.get('googleMapsLink'),
        username=data['username']
    )
    vendor.set_password(data['password'])

    db.session.add(vendor)
    db.session.commit()

    return jsonify({'message': 'Vendor registered successfully'}), 201

from flask_jwt_extended import jwt_required, get_jwt_identity

@vendor_bp.route('/vendor/profile', methods=['GET'])
@jwt_required()
def get_vendor_profile():
    current_user = get_jwt_identity()
    vendor = Vendor.query.filter_by(username=current_user).first()

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
        'googleMapsLink': vendor.google_maps_link,
        'username': vendor.username
    }), 200
