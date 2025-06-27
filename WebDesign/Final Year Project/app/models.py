from app import db, bcrypt, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(20), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    role          = db.Column(db.String(20), nullable=False, default='user')
    password_hash = db.Column(db.String(128), nullable=False)

    # One-to-many relationship: one user = many medical records
    records       = db.relationship('MedicalRecord', backref='author', lazy=True)

    def set_password(self, password):
        """Hash password using Flask-Bcrypt."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verify password against stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}, role={self.role})>"

class MedicalRecord(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    patient_name   = db.Column(db.String(100), nullable=False)
    patient_email  = db.Column(db.String(120), nullable=False)
    address        = db.Column(db.String(200), nullable=False)
    date_of_birth  = db.Column(db.Date, nullable=False)
    gender         = db.Column(db.String(10), nullable=False)
    allergies      = db.Column(db.String(200))
    medications    = db.Column(db.String(300))
    provider_name  = db.Column(db.String(100), nullable=False)
    diagnosis      = db.Column(db.Text, nullable=False)
    date_created   = db.Column(db.DateTime, default=datetime.utcnow)
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return (f"<MedicalRecord(patient={self.patient_name}, "
                f"email={self.patient_email}, provider={self.provider_name}, "
                f"created={self.date_created.date()})>")
