from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from config import Config
import logging, os
from logging.handlers import RotatingFileHandler


# ——— Extensions ———
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
limiter = Limiter(key_func=get_remote_address)
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # ——— Initialize Extensions ———
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)

    # ——— Security Headers via Talisman ———
    # Note: only one 'style-src' block below, and we explicitly allow the CDN you need
    csp = {
        'default-src': ["'self'"],
        'style-src': [
            "'self'",
            "https://fonts.googleapis.com",
            "https://cdn.jsdelivr.net",
            "https://stackpath.bootstrapcdn.com",
        ],
        'script-src': [
            "'self'",
            "https://www.google.com",
            "https://www.gstatic.com",
            "https://cdn.jsdelivr.net",
            "https://stackpath.bootstrapcdn.com",
        ],
        'frame-src': [
            "https://www.google.com",
            "https://recaptcha.google.com",
        ],
        'font-src': ["'self'", "https://fonts.gstatic.com"],
    }
    Talisman(app, content_security_policy=csp, force_https=False)

    #turned this off to check for an error, normally =csp

    #Session timeout renewal
    from datetime import datetime
    from flask import session

    @app.before_request
    def make_session_permanent():
        session.permanent = True
        session.modified = True


    # ——— Register Blueprints ———
    from app.routes import main
    app.register_blueprint(main, url_prefix='/')

    # ——— Audit Logger ———
    os.makedirs(app.instance_path, exist_ok=True)
    audit_path = os.path.join(app.instance_path, 'audit.log')
    handler = RotatingFileHandler(audit_path, maxBytes=1_000_000, backupCount=3)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False
    audit_logger.addHandler(handler)
    audit_logger.info('Application started')

    # ——— Custom 403 Error Page ———
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('403.html'), 403

    return app
