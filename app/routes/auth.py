from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.db import query_db
from app.models.user import User
from app.models.forms import RegistrationForm, LoginForm
from app.models.utils import log_activity

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Check duplicate email
        existing = query_db("SELECT id FROM users WHERE email = %s", (form.email.data,), one=True)
        if existing:
            flash('Email already registered. Please log in.', 'danger')
            return render_template('auth/register.html', form=form)

        pwd_hash = generate_password_hash(form.password.data)
        user_id = query_db(
            """INSERT INTO users (name, email, password_hash, role,
               organization_name, registration_number, phone, address)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (form.name.data, form.email.data, pwd_hash, form.role.data,
             form.organization_name.data, form.registration_number.data,
             form.phone.data, form.address.data),
            commit=True
        )
        log_activity(user_id, 'REGISTER', f"New {form.role.data} registered")
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and check_password_hash(user.password_hash, form.password.data):
            if not user.is_active_flag:
                flash('Your account has been deactivated.', 'danger')
                return render_template('auth/login.html', form=form)
            login_user(user, remember=form.remember.data)
            log_activity(user.id, 'LOGIN', 'User logged in')
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    log_activity(current_user.id, 'LOGOUT', 'User logged out')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile')
@login_required
def profile():
    donations = []
    if current_user.is_donor():
        donations = query_db(
            """SELECT d.*, c.title as campaign_title
               FROM donations d JOIN campaigns c ON d.campaign_id = c.id
               WHERE d.donor_id = %s ORDER BY d.created_at DESC""",
            (current_user.id,)
        )
    campaigns = []
    if current_user.is_ngo():
        campaigns = query_db(
            "SELECT * FROM campaigns WHERE ngo_id = %s ORDER BY created_at DESC",
            (current_user.id,)
        )
    return render_template('auth/profile.html', donations=donations, campaigns=campaigns)
