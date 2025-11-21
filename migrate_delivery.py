"""
Database Migration Script: Add Delivery Columns
Run this on Render to fix the "column does not exist" error
"""
import os
from app import create_app, db

def run_migration():
    """Add delivery columns to projects table"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Starting database migration...")
            print("Adding delivery columns to projects table...")
            
            # Add the three new columns
            db.session.execute('''
                ALTER TABLE projects 
                ADD COLUMN IF NOT EXISTS delivery_link VARCHAR(500);
            ''')
            print("✅ Added delivery_link column")
            
            db.session.execute('''
                ALTER TABLE projects 
                ADD COLUMN IF NOT EXISTS delivery_note TEXT;
            ''')
            print("✅ Added delivery_note column")
            
            db.session.execute('''
                ALTER TABLE projects 
                ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP;
            ''')
            print("✅ Added delivered_at column")
            
            # Commit changes
            db.session.commit()
            print("\n🎉 Migration completed successfully!\n")
            
            # Verify columns were added
            print("Verifying columns...")
            result = db.session.execute('''
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'projects' 
                AND column_name IN ('delivery_link', 'delivery_note', 'delivered_at')
                ORDER BY column_name;
            ''')
            
            print("\n✅ Verified Columns:")
            print("-" * 50)
            for row in result:
                print(f"  • {row[0]}: {row[1]}")
            print("-" * 50)
            print("\n✨ All done! Your site should work now.\n")
            
        except Exception as e:
            print(f"\n❌ Error during migration: {e}")
            print("Rolling back changes...")
            db.session.rollback()
            print("Migration failed. Please check the error above.")
            raise

if __name__ == '__main__':
    run_migration()
