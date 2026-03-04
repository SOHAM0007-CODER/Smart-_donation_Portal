import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()

login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)

    # ── Core Config ──────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me-in-production-abc123xyz')
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024   # 10 MB upload limit

    # ── MySQL ─────────────────────────────────────────────────────────────────
    app.config['MYSQL_HOST']     = os.getenv('MYSQL_HOST',     'localhost')
    app.config['MYSQL_USER']     = os.getenv('MYSQL_USER',     'root')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
    app.config['MYSQL_DB']       = os.getenv('MYSQL_DB',       'smart_donation_portal')
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    # ── Upload folders ────────────────────────────────────────────────────────
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    app.config['UPLOAD_FOLDER']         = os.path.join(BASE_DIR, 'static', 'uploads')
    app.config['PAYMENT_PROOF_FOLDER']  = os.path.join(BASE_DIR, 'static', 'uploads', 'payment_proofs')
    app.config['EXPENSE_PROOF_FOLDER']  = os.path.join(BASE_DIR, 'static', 'uploads', 'expense_proofs')
    app.config['CAMPAIGN_IMG_FOLDER']   = os.path.join(BASE_DIR, 'static', 'uploads', 'campaign_images')
    app.config['ALLOWED_EXTENSIONS']    = {'png', 'jpg', 'jpeg', 'pdf', 'gif'}

    for folder in [app.config['PAYMENT_PROOF_FOLDER'],
                   app.config['EXPENSE_PROOF_FOLDER'],
                   app.config['CAMPAIGN_IMG_FOLDER']]:
        os.makedirs(folder, exist_ok=True)

    # ── Extensions ───────────────────────────────────────────────────────────
    from app.models.db import mysql
    mysql.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    csrf.init_app(app)

    # ── Blueprints ────────────────────────────────────────────────────────────
    from app.routes.auth       import auth_bp
    from app.routes.campaigns  import campaigns_bp
    from app.routes.donations  import donations_bp
    from app.routes.expenses   import expenses_bp
    from app.routes.admin      import admin_bp
    from app.routes.main       import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp,      url_prefix='/auth')
    app.register_blueprint(campaigns_bp, url_prefix='/campaigns')
    app.register_blueprint(donations_bp, url_prefix='/donations')
    app.register_blueprint(expenses_bp,  url_prefix='/expenses')
    app.register_blueprint(admin_bp,     url_prefix='/admin')

    return app
