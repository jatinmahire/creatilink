from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
socketio = SocketIO()

def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, async_mode=app.config.get('SOCKETIO_ASYNC_MODE', 'eventlet'), cors_allowed_origins="*")
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    from app.projects import projects_bp
    from app.chat import chat_bp
    from app.payments import payments_bp
    from app.dashboard import dashboard_bp
    from app.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    
    # Register SocketIO events
    from app import socket_events
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Auto-seed database if empty (for free tier without shell access)
        from app.models import User, Project, Application, Package, Review, Transaction
        from datetime import datetime, timedelta
        import random
        
        admin = User.query.filter_by(email='admin@creatilink.com').first()
        
        if not admin:
            # Database is empty, seed it
            print("Database is empty,initializing with seed data...")
            
            # Create admin
            admin = User(
                full_name="Admin User",
                email="admin@creatilink.com",
                role="customer",
                is_admin=True
            )
            admin.set_password("admin123")
            db.session.add(admin)
            
            # Create sample customer
            customer = User(
                full_name="John Smith",
                email="john@example.com",
                role="customer"
            )
            customer.set_password("password123")
            db.session.add(customer)
            
            # Create sample creator
            creator = User(
                full_name="Emma Wilson",
                email="emma@example.com",
                role="creator",
                domain="graphic_design",
                bio="Professional graphic designer with 5+ years experience",
                skills="Photoshop, Illustrator, InDesign",
                rating=4.8,
                total_reviews=10
            )
            creator.set_password("password123")
            db.session.add(creator)
            
            db.session.commit()
            print("Database initialized with basic accounts!")
    
    return app
