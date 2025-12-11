"""
Local development server runner
Creates a fresh database without migration issues
"""
import os
from app import create_app, socketio, db
from app.models import User
from werkzeug.security import generate_password_hash

# Set environment to development
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

# Create app
app = create_app('default')

with app.app_context():
    # Drop all tables and recreate (fresh start)
    print("🗑️  Dropping old tables...")
    db.drop_all()
    
    print("📋 Creating fresh tables...")
    db.create_all()
    
    # Create admin user
    print("👤 Creating admin user...")
    admin = User(
        email='admin@creatilink.com',
        full_name='Admin User',
        password_hash=generate_password_hash('admin123'),
        is_admin=True,
        is_active=True,
        role='customer'  # Default role
    )
    db.session.add(admin)
    
    # Create test customer
    customer = User(
        email='customer@test.com',
        full_name='Test Customer',
        password_hash=generate_password_hash('customer123'),
        is_active=True,
        role='customer'
    )
    db.session.add(customer)
    
    # Create test creator
    creator = User(
        email='creator@test.com',
        full_name='Test Creator',
        password_hash=generate_password_hash('creator123'),
        is_active=True,
        role='creator'
    )
    db.session.add(creator)
    
    db.session.commit()
    print("✅ Database initialized successfully!")
    print("\n📝 Test Accounts:")
    print("   Admin: admin@creatilink.com / admin123")
    print("   Customer: customer@test.com / customer123")
    print("   Creator: creator@test.com / creator123")

print("\n🚀 Starting development server...")
print("📍 URL: http://localhost:5000")
print("⌨️  Press Ctrl+C to stop\n")

# Run with SocketIO
socketio.run(app, host='127.0.0.1', port=5000, debug=True, allow_unsafe_werkzeug=True)
