import os
from datetime import timedelta

class Config:
    # Core
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'devkey123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1 MB

    # Session / Cookie Security

    # Keeping this false because its local dev, this way cookies will send.
    # In production (HTTPS), i would set SECURE=True.
    SESSION_COOKIE_SECURE    = False
    REMEMBER_COOKIE_SECURE   = False

    SESSION_COOKIE_HTTPONLY  = True
    REMEMBER_COOKIE_HTTPONLY = True

    # Prevent CSRF/session issues across sub-domains
    SESSION_COOKIE_SAMESITE  = 'Lax'
    REMEMBER_COOKIE_SAMESITE = 'Lax'

    # Lifetime & protection
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    REMEMBER_COOKIE_DURATION   = timedelta(minutes=30)
    SESSION_PROTECTION         = 'strong'

    #reCAPTCHA
    RECAPTCHA_PUBLIC_KEY  = '6LfCMjUrAAAAADeXvwD2oA4XUhzOx6i6T2Wg9aQO'
    RECAPTCHA_PRIVATE_KEY = '6LfCMjUrAAAAANI_KEKSOVz3sGAP0NoDoux2x2Cf'


    RECAPTCHA_USE_SSL     = False
    RECAPTCHA_OPTIONS     = {'theme': 'light'}