#!/usr/bin/env python3
import os
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

def test_firebase():
    print("Testing Firebase initialization...")
    load_dotenv()
    try:
        if os.getenv("FIREBASE_PROJECT_ID") and os.getenv("FIREBASE_PRIVATE_KEY") and os.getenv("FIREBASE_CLIENT_EMAIL"):
            # Ensure proper newline formatting in private key
            private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n')
            
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
                "private_key": private_key,
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL", f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL').replace('@', '%40')}") if os.getenv("FIREBASE_CLIENT_EMAIL") else ""
            })
            
            firebase_admin.initialize_app(cred)
            print('✅ Firebase OK via .env variables')
            return True
        else:
            print("❌ Firebase configuration missing in .env")
            return False
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        return False

if __name__ == "__main__":
    test_firebase()
