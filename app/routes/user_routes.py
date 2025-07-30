# backend/app/routes/user_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User

user_bp = Blueprint("user", __name__)

@user_bp.route('/save-location', methods=['POST'])
@jwt_required()
def save_location():
    data = request.get_json()
    print(f"📍 User Location from frontend: {data}")

    user_id = get_jwt_identity()
    location = data.get('location')

    if not location:
        return jsonify({"msg": "Location is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    user.location = location
    db.session.commit()

    print("✅ Location saved in DB:", location)
    return jsonify({"msg": "Location saved"}), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200
