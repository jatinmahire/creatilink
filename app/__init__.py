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
        
        # Auto-migrate: Add delivery columns if they don't exist
        # This runs on every startup - perfect for free tier!
        try:
            db.session.execute("""
                ALTER TABLE projects 
                ADD COLUMN IF NOT EXISTS delivery_link VARCHAR(500),
                ADD COLUMN IF NOT EXISTS delivery_note TEXT,
                ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP;
            """)
            db.session.commit()
            print("✅ Database schema updated successfully!")
        except Exception as e:
            print(f"⚠️ Migration check: {e}")
            db.session.rollback()
    
    return app
