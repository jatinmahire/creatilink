"""
Google OAuth Database Migration
Adds google_id, auth_provider, and profile_picture fields to users table
"""

from app import create_app, db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        print("Starting Google OAuth migration...")
        
        try:
            # Add google_id column
            db.session.execute(text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(255) UNIQUE"
            ))
            print("✅ Added google_id column")
            
            # Add auth_provider column
            db.session.execute(text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(20) DEFAULT 'email'"
            ))
            print("✅ Added auth_provider column")
            
            # Add profile_picture column
            db.session.execute(text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(500)"
            ))
            print("✅ Added profile_picture column")
            
            # Make password_hash nullable (for OAuth users)
            db.session.execute(text(
                "ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL"
            ))
            print("✅ Made password_hash nullable")
            
            # Create index on google_id
            db.session.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)"
            ))
            print("✅ Created google_id index")
            
            db.session.commit()
            print("\n🎉 Google OAuth migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    migrate()
