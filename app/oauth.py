from flask import Blueprint, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, current_user
from authlib.integrations.flask_client import OAuth
from app import db
from app.models import User
import os

oauth_bp = Blueprint('oauth', __name__, url_prefix='/auth')

# Initialize OAuth
oauth = OAuth()

def init_oauth(app):
    """Initialize OAuth with Flask app"""
    oauth.init_app(app)
    
    # Register Google OAuth
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


@oauth_bp.route('/google')
def google_login():
    """Initiate Google OAuth login"""
    redirect_uri = url_for('oauth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@oauth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Get token from Google
        token = oauth.google.authorize_access_token()
        
        # Get user info from Google
        user_info = token.get('userinfo')
        
        if not user_info:
            flash('Failed to get user information from Google', 'danger')
            return redirect(url_for('auth.login'))
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        full_name = user_info.get('name')
        profile_picture = user_info.get('picture')
        
        # Check if user exists by Google ID
        user = User.query.filter_by(google_id=google_id).first()
        
        if user:
            # Existing Google user - just login
            login_user(user)
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('main.index'))
        
        # Check if user exists by email
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Email exists with password login - link Google account
            user.google_id = google_id
            user.auth_provider = 'google'
            user.profile_picture = profile_picture
            db.session.commit()
            
            login_user(user)
            flash(f'Google account linked successfully! Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('main.index'))
        
        # New user - need to choose role
        # Store Google data in session for registration
        session['google_signup'] = {
            'google_id': google_id,
            'email': email,
            'full_name': full_name,
            'profile_picture': profile_picture
        }
        
        # Redirect to role selection page
        return redirect(url_for('oauth.choose_role'))
    
    except Exception as e:
        flash(f'Google login failed: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))


@oauth_bp.route('/choose-role')
def choose_role():
    """Let Google users choose their role (customer/creator)"""
    if 'google_signup' not in session:
        flash('Invalid signup flow. Please try again.', 'danger')
        return redirect(url_for('auth.signup'))
    
    google_data = session['google_signup']
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Choose Your Role - CreatiLink</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <div class="min-h-screen flex items-center justify-center px-4">
            <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
                <div class="text-center mb-6">
                    <img src="{google_data['profile_picture']}" alt="Profile" class="w-20 h-20 rounded-full mx-auto mb-4">
                    <h2 class="text-2xl font-bold">Welcome, {google_data['full_name']}!</h2>
                    <p class="text-gray-600 mt-2">Choose how you want to use CreatiLink</p>
                </div>
                
                <div class="space-y-4">
                    <a href="/auth/google/complete?role=customer" 
                       class="block w-full bg-blue-600 text-white text-center py-3 rounded-lg hover:bg-blue-700 transition">
                        <i class="fas fa-shopping-cart mr-2"></i>
                        I'm a Customer
                        <p class="text-sm opacity-90 mt-1">I want to hire creators</p>
                    </a>
                    
                    <a href="/auth/google/complete?role=creator"
                       class="block w-full bg-purple-600 text-white text-center py-3 rounded-lg hover:bg-purple-700 transition">
                        <i class="fas fa-paint-brush mr-2"></i>
                        I'm a Creator
                        <p class="text-sm opacity-90 mt-1">I want to offer my services</p>
                    </a>
                </div>
                
                <div class="mt-6 text-center">
                    <a href="/auth/logout" class="text-gray-600 hover:text-gray-800">Cancel</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''


@oauth_bp.route('/google/complete')
def complete_google_signup():
    """Complete Google signup with role selection"""
    if 'google_signup' not in session:
        flash('Invalid signup flow. Please try again.', 'danger')
        return redirect(url_for('auth.signup'))
    
    role = request.args.get('role')
    if role not in ['customer', 'creator']:
        flash('Please select a valid role.', 'danger')
        return redirect(url_for('oauth.choose_role'))
    
    google_data = session.pop('google_signup')
    
    try:
        # Create new user
        new_user = User(
            full_name=google_data['full_name'],
            email=google_data['email'],
            google_id=google_data['google_id'],
            auth_provider='google',
            profile_picture=google_data['profile_picture'],
            role=role,
            password_hash=''  # No password for OAuth users
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Log in the user
        login_user(new_user)
        
        flash(f'Account created successfully! Welcome to CreatiLink, {new_user.full_name}!', 'success')
        return redirect(url_for('main.index'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Registration failed: {str(e)}', 'danger')
        return redirect(url_for('auth.signup'))


@oauth_bp.route('/google/unlink', methods=['POST'])
def unlink_google():
    """Unlink Google account from user profile"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if current_user.auth_provider == 'google' and not current_user.password_hash:
        flash('Cannot unlink Google - please set a password first!', 'danger')
        return redirect(url_for('main.profile'))
    
    current_user.google_id = None
    current_user.auth_provider = 'email'
    db.session.commit()
    
    flash('Google account unlinked successfully', 'success')
    return redirect(url_for('main.profile'))
