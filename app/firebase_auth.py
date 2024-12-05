import os
import firebase_admin
from firebase_admin import credentials, auth
from flask import current_app

def initialize_firebase():
    """Initialize Firebase Admin SDK with graceful fallback"""
    try:
        # Try to initialize with service account file
        cred = credentials.Certificate(os.environ.get('FIREBASE_ADMIN_SDK_PATH'))
        firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully with service account")
    except (ValueError, FileNotFoundError) as e:
        try:
            # Try to initialize with default credentials
            firebase_admin.initialize_app()
            print("Firebase initialized with default credentials")
        except Exception as e:
            # If both methods fail, just print a warning
            print("Warning: Firebase initialization failed. Some features may be unavailable.")
            print(f"Error: {str(e)}")
            # Initialize with minimal configuration for development
            if not firebase_admin._apps:
                firebase_admin.initialize_app(None)
            print("Firebase initialized with minimal configuration for development")

def verify_firebase_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying Firebase token: {e}")
        return None