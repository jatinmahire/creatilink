#!/usr/bin/env python3
"""
Manual migration script to add Google OAuth columns to users table.
Run this on Render via Shell to manually add the required columns.
"""

import os
import sys
from sqlalchemy import create_engine, text

# Get database URL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL environment variable not found!")
    sys.exit(1)

print(f"🔗 Connecting to database...")
engine = create_engine(database_url)

try:
    with engine.connect() as conn:
        print("✅ Connected to database")
        
        # Check and add google_id column
        print("\n📝 Checking google_id column...")
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='users' AND column_name='google_id'
        """))
        
        if result.fetchone():
            print("✅ google_id column already exists")
        else:
            print("➕ Adding google_id column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE;"))
            conn.commit()
            print("✅ Added google_id column")
        
        # Check and add auth_provider column
        print("\n📝 Checking auth_provider column...")
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='users' AND column_name='auth_provider'
        """))
        
        if result.fetchone():
            print("✅ auth_provider column already exists")
        else:
            print("➕ Adding auth_provider column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN auth_provider VARCHAR(20) DEFAULT 'email';"))
            conn.commit()
            print("✅ Added auth_provider column")
        
        # Check and add profile_picture column
        print("\n📝 Checking profile_picture column...")
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='users' AND column_name='profile_picture'
        """))
        
        if result.fetchone():
            print("✅ profile_picture column already exists")
        else:
            print("➕ Adding profile_picture column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(500);"))
            conn.commit()
            print("✅ Added profile_picture column")
        
        # Add index
        print("\n📝 Adding index...")
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);"))
            conn.commit()
            print("✅ Added index on google_id")
        except Exception as e:
            print(f"⚠️ Index might already exist: {e}")
        
        print("\n🎉 Google OAuth migration completed successfully!")
        print("✨ You can now use 'Sign in with Google'")
        
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
