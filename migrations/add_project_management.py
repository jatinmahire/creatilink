"""
Database migration script to add project management fields
Run this ONCE on production database before deploying new code
"""
from app import app, db
from sqlalchemy import text

def upgrade():
    """Add project deletion and leave tracking fields"""
    print("🔧 Starting migration...")
    
    with app.app_context():
        try:
            # Add deletion tracking fields
            db.session.execute(text('''
                ALTER TABLE projects 
                ADD COLUMN IF NOT EXISTS deleted_by_id INTEGER REFERENCES users(id),
                ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP,
                ADD COLUMN IF NOT EXISTS deletion_reason VARCHAR(200);
            '''))
            print("✅ Added deletion tracking fields")
            
            # Add creator leave tracking fields
            db.session.execute(text('''
                ALTER TABLE projects 
                ADD COLUMN IF NOT EXISTS creator_left BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS creator_left_at TIMESTAMP;
            '''))
            print("✅ Added creator leave tracking fields")
            
            db.session.commit()
            print("🎉 Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("PROJECT MANAGEMENT MIGRATION")
    print("=" * 60)
    upgrade()
