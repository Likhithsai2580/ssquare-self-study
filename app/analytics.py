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

@analytics.track
def track_study_material_view(material_id):
    analytics.track_event(
        'study_material_view',
        {
            'material_id': material_id,
            'user_id': current_user.id,
        }
    )

@analytics.track
def track_question_attempt(question_id, is_correct):
    analytics.track_event(
        'question_attempt',
        {
            'question_id': question_id,
            'user_id': current_user.id,
            'is_correct': is_correct,
        }
    )

@analytics.track
def track_badge_earned(badge_id):
    analytics.track_event(
        'badge_earned',
        {
            'badge_id': badge_id,
            'user_id': current_user.id,
        }
    )

@analytics.track
def track_learning_path_generated(path_id):
    analytics.track_event(
        'learning_path_generated',
        {
            'path_id': path_id,
            'user_id': current_user.id,
        }
    )
