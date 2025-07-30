#__init__.py 
from flask import Flask
from flask_cors import CORS
from .extensions import db, jwt, bcrypt ,migrate # ✅ No need to import cors from here
from .routes.auth_routes import auth_bp
from .routes.coupon_routes import coupon_bp
from flask_session import Session

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    app.config["SESSION_TYPE"] = "filesystem"  # ✅ REQUIRED
    app.config["SESSION_PERMANENT"] = False
    Session(app)  # ✅ After setting config


    # ✅ Initialize CORS directly — you don’t need `cors` extension object
    CORS(app,
            supports_credentials=True,
            resources={r"/api/*": {"origins": [
                "http://localhost:5173",
                "http://localhost:5174",
                "https://going-realtor-nasa-scheduled.trycloudflare.com",
                "https://henderson-disposal-useful-modern.trycloudflare.com",
                "https://reviews-auburn-rescue-extract.trycloudflare.com",
            ]}}
        )

    # ✅ Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # ✅ Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.vendor_profile import vendor_profile_bp
    app.register_blueprint(vendor_profile_bp)
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix="/user")

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(coupon_bp)
    # Add a root route for "/"
    @app.route("/")
    def index():
        return "EzyFix API is running!"

    return app
