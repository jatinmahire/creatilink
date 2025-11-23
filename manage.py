# CRITICAL: Gevent monkey patch MUST be first, BEFORE any imports!
# Disable SSL patching to prevent Python 3.10 SSL recursion bug on Render
from gevent import monkey
monkey.patch_all(ssl=False)

import os
from app import create_app, socketio, db

# Get config from environment
config_name = os.getenv('FLASK_ENV', 'default')
app = create_app(config_name)

# Auto-seed database for free tier (must be after app creation)
with app.app_context():
    from app.models import User
    admin = User.query.filter_by(email='admin@creatilink.com').first()
    
    if not admin:
        print("=" * 50)
        print("Database is empty, initializing...")
        print("=" * 50)
        
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
            bio="Professional graphic designer",
            skills="Photoshop, Illustrator",
            rating=4.8
        )
        creator.set_password("password123")
        db.session.add(creator)
        
        db.session.commit()
        print("=" * 50)
        print("✓ Database initialized!")
        print("=" * 50)

if __name__ == '__main__':
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(
        app,
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True,
        log_output=True
    )
