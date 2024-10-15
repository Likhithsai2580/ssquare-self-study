from flask import Blueprint, request, jsonify
from app.firebase_auth import verify_firebase_token
from app.models import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/firebase_login', methods=['POST'])
def firebase_login():
    id_token = request.json.get('idToken')
    if not id_token:
        return jsonify({'error': 'No ID token provided'}), 400

    decoded_token = verify_firebase_token(id_token)
    if not decoded_token:
        return jsonify({'error': 'Invalid ID token'}), 401

    uid = decoded_token['uid']
    email = decoded_token.get('email')

    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        user = User(firebase_uid=uid, email=email)
        db.session.add(user)
        db.session.commit()

    # Here you would typically create a session or return a JWT token
    return jsonify({'message': 'Login successful', 'user_id': user.id}), 200

# ... existing routes ...