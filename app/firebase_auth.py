import firebase_admin
from firebase_admin import credentials, auth
from flask import current_app

def initialize_firebase():
    cred = credentials.Certificate(current_app.config['FIREBASE_ADMIN_SDK_PATH'])
    firebase_admin.initialize_app(cred)

def verify_firebase_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying Firebase token: {e}")
        return None