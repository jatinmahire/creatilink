"""
Manual Google OAuth Database Migration
Visit this route on Render to add the required columns
"""
from flask import Blueprint, jsonify, render_template_string
from app import db
from sqlalchemy import text

# Create a blueprint for migration
migration_bp = Blueprint('migration', __name__)

@migration_bp.route('/setup-google-oauth-now')
def setup_google_oauth():
    """
    Visit this URL to manually add Google OAuth columns
    URL: https://creatilink-app.onrender.com/setup-google-oauth-now
    """
    try:
        results = []
        
        # Add google_id column
        try:
            db.session.execute(text("ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE;"))
            db.session.commit()
            results.append("✅ Added google_id column")
        except Exception as e:
            if "already exists" in str(e) or "duplicate" in str(e).lower():
                results.append("ℹ️ google_id column already exists")
            else:
                results.append(f"❌ google_id error: {str(e)}")
                db.session.rollback()
        
        # Add auth_provider column
        try:
            db.session.execute(text("ALTER TABLE users ADD COLUMN auth_provider VARCHAR(20) DEFAULT 'email';"))
            db.session.commit()
            results.append("✅ Added auth_provider column")
        except Exception as e:
            if "already exists" in str(e) or "duplicate" in str(e).lower():
                results.append("ℹ️ auth_provider column already exists")
            else:
                results.append(f"❌ auth_provider error: {str(e)}")
                db.session.rollback()
        
        # Add profile_picture column
        try:
            db.session.execute(text("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(500);"))
            db.session.commit()
            results.append("✅ Added profile_picture column")
        except Exception as e:
            if "already exists" in str(e) or "duplicate" in str(e).lower():
                results.append("ℹ️ profile_picture column already exists")  
            else:
                results.append(f"❌ profile_picture error: {str(e)}")
                db.session.rollback()
        
        # Add index
        try:
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);"))
            db.session.commit()
            results.append("✅ Added index on google_id")
        except Exception as e:
            results.append(f"ℹ️ Index: {str(e)}")
        
        # Create HTML response
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Google OAuth Migration</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #333; }
                .success { color: green; }
                .info { color: blue; }
                .error { color: red; }
                .result { padding: 10px; margin: 5px 0; border-left: 4px solid #ddd; }
                .button { background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; 
                         border-radius: 5px; display: inline-block; margin-top: 20px; }
            </style>
        </head>
        <body>
            <h1>🎉 Google OAuth Setup Complete!</h1>
            <div class="results">
                {% for result in results %}
                <div class="result">{{ result }}</div>
                {% endfor %}
            </div>
            <p><strong>Next steps:</strong></p>
            <ol>
                <li>Go to <a href="/">homepage</a></li>
                <li>Click "Sign in with Google"</li>
                <li>It should work now!</li>
            </ol>
            <a href="/auth/login" class="button">Try Google Login Now →</a>
        </body>
        </html>
        """
        
        return render_template_string(html, results=results)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Migration failed. Please contact support."
        }), 500
