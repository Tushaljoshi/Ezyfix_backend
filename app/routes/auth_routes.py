# auth_routes.py

from flask import Blueprint, request, jsonify
from app.models.user import User
from app.extensions import db, bcrypt
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from app.firebase import db as firestore_db # Use Firestore db
import random
import requests
import os
from flask_cors import cross_origin
from flask import session  # ✅ Add this to top
from dotenv import load_dotenv
load_dotenv()  # ✅ Load variables from .env

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")  # 👈 Add prefix

@auth_bp.route("/register", methods=["POST", "OPTIONS"])
@cross_origin()
def register():
    data = request.get_json()
    print("Received data:", data)
    try:
        if request.method == "OPTIONS":
            return '', 200

        data = request.get_json()
        required_fields = ["email", "password", "businessName", "contactPerson"]

        if not all(data.get(field) for field in required_fields):
            return jsonify({"msg": "Missing required fields"}), 400

        users_ref = firestore_db.collection("users")
        existing_users = users_ref.where("email", "==", data["email"]).get()
        if existing_users:
            return jsonify({"msg": "Email already exists"}), 400

        # ✅ Proper indentation
        user_data = {
            "email": data["email"],
            "password": data["password"],  # NOTE: hash this in production!
            "business_name": data.get("businessName"),
            "contact_person": data.get("contactPerson"),
            "phone": data.get("phone"),
            "address": data.get("streetAddress"),
            "city": data.get("city"),
            "province": data.get("province"),
            "postal_code": data.get("postalCode"),
            "maps_link": data.get("googleMapsLink"),
            "username": data.get("username")
        }

        new_user_ref = users_ref.add(user_data)
        user_id = new_user_ref[1].id  # Get Firestore doc ID

        token = create_access_token(identity=user_id)  # ✅ generate token

        return jsonify({
            "msg": "Registered successfully!",
            "token": token,
            "id": user_id,  # 👈 Firestore doc ID bhej rahe ho yeh
        }), 200

    except Exception as e:
        print("🔥 Registration error:", e)
        return jsonify({"msg": "Internal server error"}), 500



@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    users_ref = firestore_db.collection("users")
    user_docs = users_ref.where("email", "==", email).get()
    if not user_docs:
        return jsonify({"msg": "Invalid credentials"}), 401

    user_doc = user_docs[0]
    user_data = user_doc.to_dict()

    # If you stored hashed passwords, use bcrypt to check
    # For now, assuming plain text (not recommended for production)
    if user_data.get("password") != password:
        return jsonify({"msg": "Invalid credentials"}), 401

    token = create_access_token(identity=user_doc.id)
    return jsonify({
        "access_token": token,
        "vendor": {
            "id": user_doc.id
        }
    }), 200


def send_sms(phone, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {
        "authorization": FAST2SMS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "route": "otp",
        "variables_values": otp,
        "numbers": phone  # ✅ Format: 9180XXXXXXX (no +)
    }
    res = requests.post(url, json=payload, headers=headers)
    print("📤 SMS sent:", res.json())
# ✅ SEND OTP Route
@auth_bp.route("/send-otp", methods=["POST", "OPTIONS"])
@cross_origin()
def send_otp():
    print("🔥 /send-otp called") 
    if request.method == "OPTIONS":
        return '', 200

    data = request.get_json()
    phone = data.get("phone")
    if not phone:
        return jsonify({"msg": "Phone number is required"}), 400

    otp = str(random.randint(100000, 999999))
    session[f"otp_{phone}"] = otp
    formatted_phone = phone.replace("+", "")  # remove "+" if exists
    send_sms(formatted_phone, otp)
    print(f"🔐 OTP for {phone} is {otp}")  # 👈 For testing; log this

    return jsonify({"msg": "OTP sent successfully"}), 200


# ✅ VERIFY OTP Route
@auth_bp.route("/verify-otp", methods=["POST", "OPTIONS"])
@cross_origin()  # Allow CORS
def verify_otp():
    if request.method == "OPTIONS":
        return '', 200

    data = request.get_json()
    phone = data.get("phone")
    entered_otp = data.get("otp")

    stored_otp = session.get(f"otp_{phone}")
    if not stored_otp:
        return jsonify({"msg": "No OTP found for this phone"}), 400

    if entered_otp != stored_otp:
        return jsonify({"msg": "Invalid OTP"}), 400

    session.pop(f"otp_{phone}")  # ✅ Clean up after verification
    return jsonify({"msg": "Phone verified successfully"}), 200

@auth_bp.route("/update/<user_id>", methods=["PUT"])
@cross_origin()
def update_vendor(user_id):
    try:
        data = request.get_json()
        user_ref = firestore_db.collection("users").document(user_id)
        user_ref.update(data)
        return jsonify({"msg": "Vendor profile updated"}), 200
    except Exception as e:
        print("🔥 Update error:", e)
        return jsonify({"msg": "Update failed"}), 500

@auth_bp.route("/profile/<user_id>", methods=["GET"])
@cross_origin()
def get_vendor_profile(user_id):
    try:
        print("👁️‍🗨️ User ID requested:", user_id)
        user_ref = firestore_db.collection("users").document(user_id)
        doc = user_ref.get()

        if not doc.exists:
            return jsonify({"msg": "User not found"}), 404

        return jsonify(doc.to_dict()), 200

    except Exception as e:
        print("🔥 Fetch error:", e)
        return jsonify({"msg": "Error fetching profile"}), 500
