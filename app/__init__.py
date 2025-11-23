from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from sqlalchemy import text
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
    from app.payment_history import payment_history_bp
    from app.disputes import disputes_bp
    from app.oauth import oauth_bp, init_oauth
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(payment_history_bp)
    app.register_blueprint(disputes_bp)
    app.register_blueprint(oauth_bp)
    
    # Initialize OAuth
    init_oauth(app)
    
    # Register SocketIO events
    from app import socket_events
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Auto-migrate: Add payment system columns
        try:
            # Delivery columns (existing)
            db.session.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS delivery_link VARCHAR(500);"))
            db.session.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS delivery_note TEXT;"))
            db.session.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP;"))
            
            # Payment columns for users
            db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS upi_id VARCHAR(100);"))
            
            # Payment confirmation columns for transactions
            db.session.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS customer_confirmed BOOLEAN DEFAULT FALSE;"))
            db.session.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS creator_confirmed BOOLEAN DEFAULT FALSE;"))
            db.session.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS payment_confirmed_at TIMESTAMP;"))
            db.session.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS payment_screenshot VARCHAR(500);"))
            
            # Create notifications table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    type VARCHAR(50) NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    message TEXT NOT NULL,
                    project_id INTEGER REFERENCES projects(id),
                    transaction_id INTEGER REFERENCES transactions(id),
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # PHASE 1: Project Management (Delete & Leave)
            db.session.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS deleted_by_id INTEGER REFERENCES users(id);"))
            db.session.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;"))
            db.session.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS deletion_reason VARCHAR(200);"))
            db.session.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS creator_left BOOLEAN DEFAULT FALSE;"))
            db.session.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS creator_left_at TIMESTAMP;"))
            
            # PHASE 2: Payment Screenshot Upload
            db.session.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS screenshot_uploaded_at TIMESTAMP;"))
            
            # PHASE 4: Dispute Resolution
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS disputes (
                    id SERIAL PRIMARY KEY,
                    transaction_id INTEGER REFERENCES transactions(id) NOT NULL,
                    raised_by_id INTEGER REFERENCES users(id) NOT NULL,
                    dispute_type VARCHAR(50) NOT NULL,
                    description TEXT NOT NULL,
                    evidence_files TEXT,
                    status VARCHAR(20) DEFAULT 'open',
                    resolution_notes TEXT,
                    resolved_by_id INTEGER REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP
                );
            """))
            
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_disputes_transaction ON disputes(transaction_id);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_disputes_raised_by ON disputes(raised_by_id);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_disputes_status ON disputes(status);"))
            
            # PHASE 5: Google OAuth
            db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(255) UNIQUE;"))
            db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(20) DEFAULT 'email';"))
            db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(500);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);"))
            
            db.session.commit()
            print("✅ Payment system migration successful!")
            print("✅ Phase 1-5 migrations successful (including Google OAuth)!")
        except Exception as e:
            print(f"⚠️ Migration error: {e}")
            db.session.rollback()
    
    return app
