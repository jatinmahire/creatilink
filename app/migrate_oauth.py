"""
Special migration route for Google OAuth columns.
Visit /admin/migrate-oauth on your live site to run this migration.
"""

from flask import Blueprint, jsonify
from app import db
from sqlalchemy import text

migrate_bp = Blueprint('migrate', __name__)

@migrate_bp.route('/admin/migrate-oauth')
def migrate_oauth():
    """Run Google OAuth migration by visiting this URL"""
    try:
        results = []
        
        # Check and add google_id column
        result = db.session.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='users' AND column_name='google_id'
        """))
        
        if result.fetchone():
            results.append("✅ google_id column already exists")
        else:
            db.session.execute(text("ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE;"))
            db.session.commit()
            results.append("✅ Added google_id column")
        
        # Check and add auth_provider column
        result = db.session.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='users' AND column_name='auth_provider'
        """))
        
        if result.fetchone():
            results.append("✅ auth_provider column already exists")
        else:
            db.session.execute(text("ALTER TABLE users ADD COLUMN auth_provider VARCHAR(20) DEFAULT 'email';"))
            db.session.commit()
            results.append("✅ Added auth_provider column")
        
        # Check and add profile_picture column
        result = db.session.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='users' AND column_name='profile_picture'
        """))
        
        if result.fetchone():
            results.append("✅ profile_picture column already exists")
        else:
            db.session.execute(text("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(500);"))
            db.session.commit()
            results.append("✅ Added profile_picture column")
        
        # Add index
        try:
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);"))
            db.session.commit()
            results.append("✅ Added index on google_id")
        except:
            results.append("⚠️ Index might already exist")
        
        return jsonify({
            "success": True,
            "message": "Google OAuth migration completed!",
            "details": results
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
