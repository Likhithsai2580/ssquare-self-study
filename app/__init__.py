from flask import Flask
from flask_socketio import SocketIO
from flask_analytics import Analytics
from app.firebase_auth import initialize_firebase

socketio = SocketIO()
analytics = Analytics()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    from app.models import db
    db.init_app(app)
    
    from app.routes import main, auth_bp, exam_bp
    app.register_blueprint(main)
    app.register_blueprint(auth_bp)
    app.register_blueprint(exam_bp)
    
    socketio.init_app(app)
    analytics.init_app(app)
    
    with app.app_context():
        initialize_firebase()
    
    return app