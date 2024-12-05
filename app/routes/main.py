from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.analytics import track_page_view
from app.recommendation import get_recommendations
from app.models import db, StudyMaterial

main = Blueprint('main', __name__)

@main.route('/')
def index():
    track_page_view()
    return render_template('index.html')

@main.route('/study_recommendations')
@login_required
def study_recommendations():
    track_page_view()
    recommendations = get_recommendations(current_user.id, 'Mathematics')  # You can change the subject as needed
    return render_template('study_recommendations.html', recommendations=recommendations)

def create_sample_study_materials():
    """Create some sample study materials if none exist"""
    if StudyMaterial.query.first() is None:
        materials = [
            {
                'title': 'Introduction to Python',
                'content': 'Python is a high-level programming language...',
                'subject': 'Programming'
            },
            {
                'title': 'Basic Mathematics',
                'content': 'Mathematics is the foundation of all sciences...',
                'subject': 'Mathematics'
            },
            {
                'title': 'English Grammar',
                'content': 'Grammar is the foundation of language...',
                'subject': 'English'
            }
        ]
        
        for material in materials:
            study_material = StudyMaterial(**material)
            db.session.add(study_material)
        
        db.session.commit()
        print("Created sample study materials")