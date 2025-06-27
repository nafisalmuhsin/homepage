import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import RegistrationForm, LoginForm, MedicalRecordForm
from app.models import User, MedicalRecord
from app import db, bcrypt
from app import limiter
from functools import wraps
from flask_wtf.csrf import generate_csrf

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied: Admins only.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

main = Blueprint('main', __name__)
audit_logger = logging.getLogger('audit')

@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html')

@main.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()

  #Activate when I have errors>  print("Submitted:", form.validate_on_submit(), form.errors)

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='user',
            password_hash=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        audit_logger.info(f"User registered: user_id={user.id}, email={user.email}")
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()

   #Activate when I have errors>  print("Submitted:", form.validate_on_submit(), form.errors)

   #Log SQL injection attempt to my audit logger
    if form.email.data and form.password.data:
        if "' OR '" in form.email.data or "' OR '" in form.password.data:
            audit_logger.warning(f"SQLi Attempt Detected in login form: email={form.email.data}")

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            audit_logger.info(f"Login: user_id={user.id}, email={user.email}")
            return redirect(url_for('main.dashboard'))
        audit_logger.warning(f"Failed login attempt: email={form.email.data}")
        flash('Login unsuccessful.', 'danger')
    return render_template('login.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@main.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Access denied: Admins only.', 'danger')
        return redirect(url_for('main.dashboard'))
    users = User.query.all()
    csrf_token = generate_csrf()
    return render_template('admin.html', users=users, csrf_token=csrf_token)

@main.route('/admin/change_role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def change_role(user_id):
    if user_id == current_user.id:
        flash("You can't change your own role.", 'warning')
        return redirect(url_for('main.admin'))

    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')

    if new_role not in ['user', 'admin']:
        flash('Invalid role.', 'warning')
        return redirect(url_for('main.admin'))

    old_role = user.role
    user.role = new_role
    db.session.commit()

    audit_logger.info(f"Role Change: admin_id={current_user.id}, target_user_id={user.id}, from={old_role} to={new_role}")
    flash(f"Role updated: {user.username} is now a {new_role}.", 'success')
    return redirect(url_for('main.admin'))

@main.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if current_user.id == user_id:
        flash("You cannot delete your own account while logged in.", "danger")
        return redirect(url_for('main.admin'))

    user = User.query.get_or_404(user_id)

    user_records = MedicalRecord.query.filter_by(user_id=user.id).all()
    for record in user_records:
        db.session.delete(record)

    db.session.delete(user)
    db.session.commit()

    audit_logger.info(f"Admin {current_user.username} (id={current_user.id}) deleted user '{user.username}' (id={user.id})")
    flash(f"User '{user.username}' and their records have been deleted.", "success")
    return redirect(url_for('main.admin'))

@main.route('/records', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def records():
    form = MedicalRecordForm()
    if form.validate_on_submit():
        record = MedicalRecord(
            patient_name=form.patient_name.data,
            patient_email=form.patient_email.data,
            address=form.address.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            allergies=form.allergies.data,
            medications=form.medications.data,
            provider_name=form.provider_name.data,
            diagnosis=form.diagnosis.data,
            author=current_user
        )
        db.session.add(record)
        db.session.commit()
        audit_logger.info(f"Create Record: user_id={current_user.id}, record_id={record.id}")
        flash('Record added.', 'success')
        return redirect(url_for('main.records'))

    user_records = MedicalRecord.query.filter_by(author=current_user).all()
    return render_template('records.html', form=form, records=user_records)

@main.route('/record/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
@limiter.limit("5 per minute")
def edit_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)

    if record.author != current_user and current_user.role != 'admin':
        audit_logger.warning(f"403 Forbidden (edit): user_id={current_user.id}, record_id={record.id}")
        abort(403)

    form = MedicalRecordForm(obj=record)
    if form.validate_on_submit():
        record.patient_name = form.patient_name.data
        record.patient_email = form.patient_email.data
        record.address = form.address.data
        record.date_of_birth = form.date_of_birth.data
        record.gender = form.gender.data
        record.allergies = form.allergies.data
        record.medications = form.medications.data
        record.provider_name = form.provider_name.data
        record.diagnosis = form.diagnosis.data
        db.session.commit()
        audit_logger.info(f"Update Record: user_id={current_user.id}, record_id={record.id}")
        flash('Record updated.', 'success')
        return redirect(url_for('main.records'))

    return render_template('edit_record.html', form=form, record=record)

@main.route('/record/delete/<int:record_id>', methods=['POST'])
@login_required
@limiter.limit("5 per minute")
def delete_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)

    if record.author != current_user and current_user.role != 'admin':
        audit_logger.warning(f"403 Forbidden (delete): user_id={current_user.id}, record_id={record.id}")
        abort(403)

    db.session.delete(record)
    db.session.commit()
    audit_logger.info(f"Delete Record: user_id={current_user.id}, record_id={record.id}")
    flash('Record deleted.', 'success')
    return redirect(url_for('main.records'))

@main.route('/admin/records')
@login_required
def admin_records():
    if current_user.role != 'admin':
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for('main.dashboard'))

    q = request.args.get('q', '', type=str).strip()

    if q:
        records = (MedicalRecord.query
                   .join(User, MedicalRecord.author)
                   .filter(
                       db.or_(
                           MedicalRecord.patient_name.ilike(f"%{q}%"),
                           User.username.ilike(f"%{q}%")
                       )
                   )
                   .all())
    else:
        records = MedicalRecord.query.all()

    return render_template('admin_records.html', records=records, q=q)


@main.route('/admin/records/print')
@login_required
def print_records():
    if current_user.role != 'admin':
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for('main.dashboard'))

    q = request.args.get('q', '', type=str).strip()

    if q:
        records = (MedicalRecord.query
                   .join(User, MedicalRecord.author)
                   .filter(
                       db.or_(
                           MedicalRecord.patient_name.ilike(f"%{q}%"),
                           User.username.ilike(f"%{q}%")
                       )
                   )
                   .all())
    else:
        records = MedicalRecord.query.all()

    return render_template('print_records.html', records=records, q=q)

@main.route('/logout')
@login_required
def logout():
    user_id = current_user.id
    logout_user()
    audit_logger.info(f"Logout: user_id={user_id}")
    flash('Logged out.', 'info')
    return redirect(url_for('main.home'))
