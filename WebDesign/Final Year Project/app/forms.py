import bleach
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
    StringField, PasswordField, SubmitField,
    BooleanField, TextAreaField, DateField, SelectField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, ValidationError, Regexp
)
from app.models import User

def clean_text(x):
    return bleach.clean(x) if x else ''

class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=20)],
        filters=[clean_text]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        filters=[clean_text]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8, message='Password must be at least 8 characters long.'),
            Regexp(r'.*[A-Z].*', message='Password must include at least one uppercase letter.'),
            Regexp(r'.*[a-z].*', message='Password must include at least one lowercase letter.'),
            Regexp(r'.*\d.*', message='Password must include at least one number.'),
            Regexp(r'.*[^A-Za-z0-9].*', message='Password must include at least one special character.')
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )
    recaptcha = RecaptchaField()
    submit = SubmitField('Register')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email already in use.')

class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        filters=[clean_text]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    remember = BooleanField('Remember Me')
    recaptcha = RecaptchaField()
    submit = SubmitField('Login')

class MedicalRecordForm(FlaskForm):
    patient_name   = StringField(
        'Patient Name',
        validators=[DataRequired(), Length(max=100)],
        filters=[clean_text]
    )
    patient_email  = StringField(
        'Patient Email',
        validators=[DataRequired(), Email(), Length(max=120)],
        filters=[clean_text]
    )
    address        = StringField(
        'Address',
        validators=[DataRequired(), Length(max=200)],
        filters=[clean_text]
    )
    date_of_birth  = DateField(
        'Date of Birth',
        validators=[DataRequired()],
        format='%Y-%m-%d'
    )
    gender         = SelectField(
        'Gender',
        choices=[('Male','Male'),('Female','Female'),('Other','Other')],
        validators=[DataRequired()]
    )
    allergies      = StringField(
        'Allergies',
        validators=[Length(max=200)],
        filters=[clean_text]
    )
    medications    = StringField(
        'Current Medications',
        validators=[Length(max=300)],
        filters=[clean_text]
    )
    provider_name  = StringField(
        'Provider/Doctor Name',
        validators=[DataRequired(), Length(max=100)],
        filters=[clean_text]
    )
    diagnosis      = TextAreaField(
        'Diagnosis',
        validators=[DataRequired(), Length(max=2000)],
        filters=[clean_text]
    )
    submit = SubmitField('Save Record')
