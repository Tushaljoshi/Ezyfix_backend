# backend/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user import User  # tumhara user model
from app.extensions import db
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/signup', methods=['POST', 'OPTIONS'])
def signup():
    data = request.get_json()

    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"message": "Email already registered"}), 400

    new_user = User(
        name=f"{data['firstName']} {data['lastName']}",
        username=data['username'],
        email=data['email'],
        phone=data['phone'],
        password=generate_password_hash(data['password']),
        wallet=0,
        avatar=f"https://i.pravatar.cc/150?u={data['email']}"
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Account created successfully!"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "wallet": user.wallet,
            "avatar": user.avatar
        }
    }), 200
