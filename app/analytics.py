from flask import request
from flask_login import current_user
from datetime import datetime

def track_event(event_name, data=None):
    """Track an analytics event"""
    if data is None:
        data = {}
    
    event_data = {
        'event': event_name,
        'timestamp': datetime.utcnow(),
        'user_id': current_user.id if current_user.is_authenticated else None,
        'url': request.path,
        'referrer': request.referrer,
        **data
    }
    
    # For now, just print the event data
    print(f"Analytics Event: {event_data}")
    # TODO: Implement actual analytics tracking (e.g., to a database or external service)

def track_page_view():
    track_event('page_view')

def track_exam_start(exam_id):
    track_event('exam_start', {'exam_id': exam_id})

def track_exam_complete(exam_id, score):
    track_event('exam_complete', {
        'exam_id': exam_id,
        'score': score
    })

def track_study_material_view(material_id):
    track_event('study_material_view', {'material_id': material_id})

def track_question_attempt(question_id, is_correct):
    track_event('question_attempt', {
        'question_id': question_id,
        'is_correct': is_correct
    })

def track_badge_earned(badge_id):
    track_event('badge_earned', {'badge_id': badge_id})

def track_learning_path_generated(path_id):
    track_event('learning_path_generated', {'path_id': path_id})
