from app.routes.main import main, create_sample_study_materials
from app.routes.auth import auth_bp
from app.routes.exam import exam_bp
from app.routes.api import api_bp

__all__ = ['main', 'auth_bp', 'exam_bp', 'api_bp', 'create_sample_study_materials'] 