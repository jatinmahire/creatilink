"""
Quick diagnostic to check Google OAuth credentials
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=" * 60)
print("GOOGLE OAUTH CREDENTIALS CHECK")
print("=" * 60)

# Check if .env file exists
env_path = os.path.join(os.getcwd(), '.env')
print(f"\n.env file exists: {os.path.exists(env_path)}")

# Check credentials
client_id = os.getenv('GOOGLE_CLIENT_ID')
client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

print(f"\nGOOGLE_CLIENT_ID exists: {bool(client_id)}")
if client_id:
    print(f"Value: {client_id[:30]}...")
else:
    print("❌ MISSING!")

print(f"\nGOOGLE_CLIENT_SECRET exists: {bool(client_secret)}")
if client_secret:
    print(f"Value: {client_secret[:20]}...")
else:
    print("❌ MISSING!")

print("\n" + "=" * 60)

if client_id and client_secret:
    print("✅ OAuth should work!")
else:
    print("❌ Add to .env:")
    print("GOOGLE_CLIENT_ID=90724013978-blk0ika7vt88ngqajr8j45g6b1k5va2r.apps.googleusercontent.com")
    print("GOOGLE_CLIENT_SECRET=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")
