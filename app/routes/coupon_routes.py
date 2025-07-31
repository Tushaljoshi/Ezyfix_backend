#backend/app/routes/coupon_routes.py
import requests
from flask import Blueprint, request, jsonify
from app.models.coupon import Coupon
from app.extensions import db
from app.firebase import db as firestore_db  # Add this import
import random
import os
from werkzeug.utils import secure_filename
from flask import current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.vendor import Vendor
from math import radians, cos, sin, sqrt, atan2
coupon_bp = Blueprint("coupon", __name__, url_prefix="/api/coupons")

# 🔹 Utility: Generate a 4-digit redemption code
def generate_redemption_code():
    return str(random.randint(1000, 9999))

# ✅ 1. Create a new coupon

@coupon_bp.route("/create", methods=["POST"])
@jwt_required()
def create_coupon():
    vendor_id = get_jwt_identity() 
    data = request.form
    image_file = request.files.get("companyLogo")
    category = request.form.get("category")


    image_url = None
    if image_file:
        # Save the image to a folder like /static/uploads/
        filename = secure_filename(image_file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)  # create folder if not exist
        file_path = os.path.join(upload_folder, filename)
        image_file.save(file_path)
        
        # URL to access the image
        image_url = f"https://ezyfix-backend.onrender.com/static/uploads/{filename}"

    coupon_data = {
        "title": data.get("couponTitle"),
        "description": data.get("description"),
        "category": category,
        "discount_type": data.get("discountType"),
        "discount_value": data.get("discountValue"),
        "minimum_purchase": data.get("minimumPurchase"),
        "terms_and_conditions": data.get("termsAndConditions"),
        "activation_date": data.get("activationDate"),
        "expiration_date": data.get("expirationDate"),
        "image_url": image_url,
        "status": "active",
        "vendor_id": vendor_id,
        "price": float(data.get("price", 0.0)),
        
    }

    # Add to Firestore
    doc_ref = firestore_db.collection("coupons").add(coupon_data)
    coupon_id = doc_ref[1].id if isinstance(doc_ref, tuple) else doc_ref.id

    print("🎯 Generated coupon_id:", coupon_id)

    return jsonify({
        "message": "Coupon created successfully",
        "coupon_id": coupon_id
    }), 200

def get_business_name_by_id(vendor_id):
    user_ref = firestore_db.collection('users').document(vendor_id)
    user_doc = user_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return user_data.get('business_name', '')
    return ''



def get_location_from_maps_link(maps_link):
    try:
        if not maps_link:
            return {}

        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={maps_link}&key={api_key}"
        response = requests.get(geocode_url)
        data = response.json()

        if data["status"] != "OK":
            return {}

        address_components = data["results"][0]["address_components"]

        location = {
            "city": "",
            "state": "",
            "area": ""
        }

        for comp in address_components:
            if "locality" in comp["types"]:
                location["city"] = comp["long_name"]
            elif "administrative_area_level_1" in comp["types"]:
                location["state"] = comp["long_name"]
            elif "sublocality" in comp["types"] or "neighborhood" in comp["types"]:
                location["area"] = comp["long_name"]

        return location
    except Exception as e:
        print("📛 Error parsing maps_link location:", str(e))
        return {}

def get_maps_link_by_id(vendor_id):
    user_ref = firestore_db.collection('users').document(vendor_id)
    user_doc = user_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return user_data.get('maps_link', '')
    return ''


@coupon_bp.route("/my-coupons", methods=["GET"])
@jwt_required()
def get_vendor_coupons():
    vendor_id = get_jwt_identity()
    coupons_ref = firestore_db.collection("coupons").where("vendor_id", "==", vendor_id).get()
    
    result = []
    for doc in coupons_ref:
        c = doc.to_dict()
        result.append({
            "id": doc.id,
            "couponId": doc.id,
            "title": c.get("title"),
            "description": c.get("description"),
            "discountType": c.get("discount_type"),
            "discountValue": c.get("discount_value"),
            "minimumPurchase": c.get("minimum_purchase"),
            "termsAndConditions": c.get("terms_and_conditions"),
            "activationDate": c.get("activation_date"),
            "expirationDate": c.get("expiration_date"),
            "image": c.get("image_url"),
            "category": c.get("category"),
            "status": c.get("status"),
            "price": c.get("price", 0.0)
        })
    return jsonify(result), 200


# ✅ 2. Get all coupons
@coupon_bp.route("/", methods=["GET"])
def get_all_coupons():
    user_maps_link = request.args.get("maps_link")
    user_location = get_location_from_maps_link(user_maps_link) if user_maps_link else {}

    print("📍 User Location:", user_location)

    coupons_ref = firestore_db.collection("coupons").get()
    result = []
    for doc in coupons_ref:
        c = doc.to_dict()
        vendor_id = c.get("vendor_id", None)
        maps_link = get_maps_link_by_id(vendor_id)
        location_data = get_location_from_maps_link(maps_link)
        
        if user_location:
            coupon_city = location_data.get("city", "").lower()
            coupon_state = location_data.get("state", "").lower()
            coupon_area = location_data.get("area", "").lower()

            user_city = user_location.get("city", "").lower()
            user_state = user_location.get("state", "").lower()
            user_area = user_location.get("area", "").lower()

            if not (
                user_city in coupon_city or
                user_state in coupon_state or
                user_area in coupon_area
            ):
                continue  # 🔁 skip this coupon if not matched

        result.append({
            "id": doc.id,
            "couponId": doc.id,
            "title": c.get("title"),
            "description": c.get("description"),
            "business_name": get_business_name_by_id(vendor_id),
            "maps_link": maps_link,
            "location": location_data,
            "discountType": c.get("discount_type"),
            "discountValue": c.get("discount_value"),
            "minimumPurchase": c.get("minimum_purchase"),
            "termsAndConditions": c.get("terms_and_conditions"),
            "activationDate": c.get("activation_date"),
            "expirationDate": c.get("expiration_date"),
            "image": c.get("image_url"),
            "category": c.get("category"),
            "status": c.get("status"),
            "purchased": 1 if c.get("status") == "purchased" else 0,
            "redeemed": 1 if c.get("status") == "redeemed" else 0,
            "tag": c.get("discount_type") or "General",
            "price": c.get("price", 0.0),
            "badge": "Hot" if c.get("status") == "active" else "Limited"
        })
    return jsonify(result), 200


# ✅ 3. Get, Update, or Delete a single coupon
@coupon_bp.route("/<string:coupon_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def handle_coupon(coupon_id):
    coupon_ref = firestore_db.collection("coupons").document(coupon_id)

    if request.method == "GET":
        vendor_id = get_jwt_identity()
        doc = coupon_ref.get()
        if not doc.exists:
            return jsonify({"error": "Coupon not found"}), 404
        
        coupon = doc.to_dict()
        if coupon.get("vendor_id") != vendor_id:
            return jsonify({"error": "Unauthorized"}), 403
        c = doc.to_dict()
        return jsonify({
            "id": doc.id,
            "couponId": doc.id,
            "title": c.get("title"),
            "description": c.get("description"),
            "discount_type": c.get("discount_type"),
            "discount_value": c.get("discount_value"),
            "minimum_purchase": c.get("minimum_purchase"),
            "terms_and_conditions": c.get("terms_and_conditions"),
            "activation_date": c.get("activation_date"),
            "expiration_date": c.get("expiration_date"),
            "image_url": c.get("image_url"),
            "price": c.get("price", 0.0),
            "category": c.get("category"),
            "status": c.get("status")
        }), 200

    elif request.method == "PUT":
        vendor_id = get_jwt_identity()
        doc = coupon_ref.get()
        if not doc.exists:
            return jsonify({"error": "Coupon not found"}), 404

        coupon = doc.to_dict()
        if coupon.get("vendor_id") != vendor_id:
            return jsonify({"error": "Unauthorized"}), 403

        data = request.form
        update_data = {
            "title": data.get("title"),
            "description": data.get("description"),
            "discount_type": data.get("discount_type"),
            "discount_value": data.get("discount_value"),
            "minimum_purchase": data.get("minimum_purchase"),
            "terms_and_conditions": data.get("terms_and_conditions"),
            "activation_date": data.get("activation_date"),
            "expiration_date": data.get("expiration_date"),
            "category": data.get("category"),
            "status": data.get("status"),
            "price": float(data.get("price")) if data.get("price") else None
        }
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        # Handle image update if provided
        if 'image' in request.files:
            image = request.files['image']
            filename = secure_filename(image.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            image.save(file_path)
            update_data["image_url"] = f"/static/uploads/{filename}"

        coupon_ref.update(update_data)
        return jsonify({"message": "Coupon updated successfully"}), 200

    elif request.method == "DELETE":
        vendor_id = get_jwt_identity()
        doc = coupon_ref.get()
        if not doc.exists:
            return jsonify({"error": "Coupon not found"}), 404
        
        coupon = doc.to_dict()
        if coupon.get("vendor_id") != vendor_id:
            return jsonify({"error": "Unauthorized"}), 403
    
        coupon_ref.delete()
        return jsonify({"message": "Coupon deleted successfully"}), 200

# ✅ 4. Purchase coupon
@coupon_bp.route('/purchase/<string:coupon_code>', methods=['POST'])
def purchase_coupon(coupon_code):                       # 1
    data = request.get_json()  
    print("📥 Raw purchase data:", data)
    if not data:                                        # 3
        return jsonify({'error': 'Invalid or missing JSON body'}), 400

    user_id = data.get('user_id')                       # 5
    business_id = data.get('business_id')               # 6
    
    print("👤 user_id:", user_id)
    print("🏢 business_id:", business_id)


    if not user_id or not business_id:                  # 7
        return jsonify({'error': 'user_id and business_id are required'}), 400

    coupon = Coupon.query.filter_by(code=coupon_code).first()  
    print("🎫 Coupon from SQL:", coupon)

    if not coupon:                                                  # 10
        return jsonify({'error': 'Invalid coupon code'}), 400

    user = User.query.get(user_id)
    print("👛 User coin balance:", user.coin_balance)
    print("🪙 Coupon coin cost:", coupon.coin_cost)
# 12
    if not user or user.coin_balance is None or user.coin_balance < coupon.coin_cost:  # 13
        return jsonify({'error': 'Insufficient coin balance'}), 400

    user.coin_balance -= coupon.coin_cost                          # 15
    db.session.commit() 
    # ✅ Also update Firestore coupon status to "purchased"
    firestore_coupon_ref = firestore_db.collection("coupons").document(coupon.code)
    firestore_coupon_ref.update({"status": "purchased"})


    new_user_coupon = UserCoupon(                                  # 18
        user_id=user_id,
        coupon_id=coupon.id,
        business_id=business_id
    )
    db.session.add(new_user_coupon)                                # 22
    db.session.commit()                                            # 23
    
    print("✅ Purchase successful for user_id:", user_id, "coupon:", coupon.code)


    return jsonify({                                               # 25
        'message': 'Coupon purchased successfully',
        'new_balance': user.coin_balance,
        'coupon_code': coupon.code
    }), 200

    
# ✅ 5. Redeem coupon
@coupon_bp.route("/redeem", methods=["POST"])
def redeem_coupon():
    data = request.get_json()
    coupon_id = data.get("coupon_id")
    code = data.get("redemption_code")

    if not coupon_id or not code:
        return jsonify({"error": "Missing data"}), 400

    coupon_ref = firestore_db.collection("coupons").document(coupon_id)
    doc = coupon_ref.get()
    if not doc.exists:
        return jsonify({"error": "Coupon not found"}), 404

    coupon = doc.to_dict()
    if coupon.get("redemption_code") != code:
        return jsonify({"error": "Invalid redemption code"}), 403

    if coupon.get("status") != "purchased":
        return jsonify({"error": "Coupon is not eligible for redemption"}), 400
    
    coupon_ref.update({"status": "redeemed"})
    
    return jsonify({"message": "Coupon redeemed successfully!"}), 200

@coupon_bp.route('/update-purchase', methods=['POST'])
def update_purchase():
    data = request.get_json()
    coupon_id = data.get('couponId')

    if not coupon_id:
        return jsonify({"message": "Coupon ID missing"}), 400

    coupon = Coupon.query.get(coupon_id)
    if not coupon:
        return jsonify({"message": "Coupon not found"}), 404

    coupon.purchased = coupon.purchased + 1
    db.session.commit()
    return jsonify({"message": "✅ Purchase count updated"}), 200


@coupon_bp.route('/update-redeem', methods=['POST'])
def update_redeem():
    data = request.get_json()
    coupon_id = data.get('couponId')

    if not coupon_id:
        return jsonify({"message": "Coupon ID missing"}), 400

    coupon = Coupon.query.get(coupon_id)
    if not coupon:
        return jsonify({"message": "Coupon not found"}), 404

    coupon.redeemed = coupon.redeemed + 1
    db.session.commit()
    return jsonify({"message": "✅ Redeem count updated"}), 200

@coupon_bp.route("/vendor/redeemed-coupons", methods=["GET", "OPTIONS"])
@jwt_required()
def get_redeemed_coupons():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight passed"}), 200

    vendor_id = get_jwt_identity()
    redeemed_coupons = firestore_db.collection("coupons")\
        .where("vendor_id", "==", vendor_id)\
        .where("status", "==", "redeemed")\
        .get()
    
    result = []
    for doc in redeemed_coupons:
        c = doc.to_dict()
        result.append({
            "id": doc.id,
            "title": c.get("title"),
            "category": c.get("category"),
            "status": c.get("status"),
            "price": c.get("price"),
            "redemption_code": c.get("redemption_code"),
            "image": c.get("image_url"),
            "expirationDate": c.get("expiration_date"),
        })

    return jsonify(result), 200

def haversine_distance(lat1, lng1, lat2, lng2):
    R = 6371  # Earth radius in kilometers

    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c  # in kilometers


@coupon_bp.route("/nearby", methods=["POST"])
def get_coupons_near_user():
    data = request.get_json()
    user_lat = data.get("latitude")
    user_lng = data.get("longitude")

    if user_lat is None or user_lng is None:
        return jsonify({"msg": "Latitude and Longitude required"}), 400

    try:
        user_lat = float(user_lat)
        user_lng = float(user_lng)
    except ValueError:
        return jsonify({"msg": "Invalid coordinates"}), 400

    all_coupons = firestore_db.collection("coupons").get()
    result = []

    for doc in all_coupons:
        c = doc.to_dict()
        vendor_id = c.get("vendor_id")
        maps_link = get_maps_link_by_id(vendor_id)

        if not maps_link:
            continue

        try:
            # Example: https://www.google.com/maps/place/.../@26.8467,80.9462,...
            coords_part = maps_link.split("/@")[1].split(",")
            vendor_lat = float(coords_part[0])
            vendor_lng = float(coords_part[1])
        except Exception as e:
            print("📛 Couldn't parse vendor map_link:", e)
            continue

        distance = haversine_distance(user_lat, user_lng, vendor_lat, vendor_lng)
        if distance <= 15:  # within 15 km radius
            result.append({
                "id": doc.id,
                "couponId": doc.id,
                "title": c.get("title"),
                "description": c.get("description"),
                "business_name": get_business_name_by_id(vendor_id),
                "maps_link": maps_link,
                "distance_km": round(distance, 2),
                "discountType": c.get("discount_type"),
                "discountValue": c.get("discount_value"),
                "minimumPurchase": c.get("minimum_purchase"),
                "termsAndConditions": c.get("terms_and_conditions"),
                "activationDate": c.get("activation_date"),
                "expirationDate": c.get("expiration_date"),
                "image": c.get("image_url"),
                "category": c.get("category"),
                "status": c.get("status"),
                "price": c.get("price", 0.0)
            })

    return jsonify({"coupons": result}), 200
