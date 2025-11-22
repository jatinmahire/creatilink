"""
Database migration script for payment screenshot timestamp
Run this ONCE on production database
"""
from app import app, db
from sqlalchemy import text

def upgrade():
    """Add screenshot upload timestamp field"""
    print("🔧 Starting Phase 2 migration...")
    
    with app.app_context():
        try:
            # Add screenshot timestamp field
            db.session.execute(text('''
                ALTER TABLE transactions 
                ADD COLUMN IF NOT EXISTS screenshot_uploaded_at TIMESTAMP;
            '''))
            print("✅ Added screenshot_uploaded_at field")
            
            db.session.commit()
            print("🎉 Phase 2 migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("PHASE 2: PAYMENT SCREENSHOT MIGRATION")
    print("=" * 60)
    upgrade()
