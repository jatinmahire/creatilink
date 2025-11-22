from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import User, Upload

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')  # 'customer' or 'creator'
        
        # Validation
        if not all([full_name, email, password, role]):
            flash('All fields are required.', 'danger')
            return render_template('auth/signup.html')
        
        if role not in ['customer', 'creator']:
            flash('Invalid role selected.', 'danger')
            return render_template('auth/signup.html')
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return render_template('auth/signup.html')
        
        # Create new user
        user = User(
            full_name=full_name,
            email=email,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        
        # If creator, redirect to profile setup
        if role == 'creator':
            login_user(user)
            return redirect(url_for('auth.profile_setup'))
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated.', 'danger')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            
            # Redirect based on role
            if next_page:
                return redirect(next_page)
            elif user.role == 'customer':
                return redirect(url_for('dashboard.customer_dashboard'))
            elif user.role == 'creator':
                return redirect(url_for('dashboard.creator_dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile-setup', methods=['GET', 'POST'])
@login_required
def profile_setup():
    """Creator profile setup (first-time)"""
    if current_user.role != 'creator':
        flash('This page is for creators only.', 'warning')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        from flask import current_app
        
        current_user.domain = request.form.get('domain')
        current_user.bio = request.form.get('bio')
        current_user.skills = request.form.get('skills')
        current_user.location = request.form.get('location')
        
        # Handle portfolio uploads
        if 'portfolio_files' in request.files:
            files = request.files.getlist('portfolio_files')
            for file in files:
                if file and file.filename and allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                    filename = secure_filename(file.filename)
                    # Add timestamp to avoid collisions
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    filename = f"{current_user.id}_{timestamp}_{filename}"
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    # Determine file type
                    ext = filename.rsplit('.', 1)[1].lower()
                    if ext in ['jpg', 'jpeg', 'png', 'gif']:
                        file_type = 'image'
                    elif ext in ['mp4', 'mov', 'avi']:
                        file_type = 'video'
                    else:
                        file_type = 'document'
                    
                    # Create Upload record
                    upload = Upload(
                        owner_id=current_user.id,
                        file_path=f'/static/uploads/{filename}',
                        file_type=file_type,
                        file_size=os.path.getsize(filepath),
                        original_filename=file.filename,
                        upload_type='portfolio'
                    )
                    db.session.add(upload)
        
        db.session.commit()
        flash('Profile setup complete!', 'success')
        return redirect(url_for('dashboard.creator_dashboard'))
    
    return render_template('auth/profile_setup.html')


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and edit user profile"""
    if request.method == 'POST':
        from flask import current_app
        
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.location = request.form.get('location', current_user.location)
        
        if current_user.role == 'creator':
            current_user.bio = request.form.get('bio', current_user.bio)
            current_user.skills = request.form.get('skills', current_user.skills)
            current_user.domain = request.form.get('domain', current_user.domain)
            upi_id = request.form.get('upi_id', '').strip()
            if upi_id:
                current_user.upi_id = upi_id
        
        # Handle profile image
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
                filename = secure_filename(file.filename)
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"profile_{current_user.id}_{timestamp}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                current_user.profile_image = f'/static/uploads/{filename}'
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')
