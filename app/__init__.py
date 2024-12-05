from flask import Flask
from flask_socketio import SocketIO
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from app.models import db

socketio = SocketIO()
cache = Cache(config={'CACHE_TYPE': 'simple'})
limiter = Limiter(key_func=get_remote_address)
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)
    
    from app.routes.main import main
    from app.routes.auth import auth_bp
    from app.routes.exam import exam_bp
    from app.routes.api import api_bp
    app.register_blueprint(main)
    app.register_blueprint(auth_bp)
    app.register_blueprint(exam_bp)
    app.register_blueprint(api_bp)
    
    socketio.init_app(app)
    
    from app.firebase_auth import initialize_firebase
    with app.app_context():
        db.create_all()
        initialize_firebase()
    
    return app