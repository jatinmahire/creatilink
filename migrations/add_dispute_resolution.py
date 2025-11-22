"""
Database migration script for dispute resolution system
Run this ONCE on production database
"""
from app import app, db
from sqlalchemy import text

def upgrade():
    """Create disputes table"""
    print("🔧 Starting Phase 4 migration...")
    
    with app.app_context():
        try:
            # Create disputes table
            db.session.execute(text('''
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
            '''))
            print("✅ Created disputes table")
            
            # Create indexes for better performance
            db.session.execute(text('''
                CREATE INDEX IF NOT EXISTS idx_disputes_transaction ON disputes(transaction_id);
                CREATE INDEX IF NOT EXISTS idx_disputes_raised_by ON disputes(raised_by_id);
                CREATE INDEX IF NOT EXISTS idx_disputes_status ON disputes(status);
            '''))
            print("✅ Created indexes")
            
            db.session.commit()
            print("🎉 Phase 4 migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("PHASE 4: DISPUTE RESOLUTION MIGRATION")
    print("=" * 60)
    upgrade()
