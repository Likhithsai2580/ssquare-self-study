from app import analytics
from flask import request, g
from flask_login import current_user

@analytics.track
def track_page_view():
    analytics.track_event(
        'page_view',
        {
            'url': request.path,
            'user_id': current_user.id if current_user.is_authenticated else None,
            'referrer': request.referrer,
        }
    )

@analytics.track
def track_exam_start(exam_id):
    analytics.track_event(
        'exam_start',
        {
            'exam_id': exam_id,
            'user_id': current_user.id,
        }
    )

@analytics.track
def track_exam_complete(exam_id, score):
    analytics.track_event(
        'exam_complete',
        {
            'exam_id': exam_id,
            'user_id': current_user.id,
            'score': score,
        }
    )

# Add more tracking functions as needed