from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db, cache, limiter
from app.models import Exam, UserExam
from datetime import datetime
from app.utils import calculate_score, award_points

exam_bp = Blueprint('exam', __name__)

@exam_bp.route('/exams')
@login_required
@cache.cached(timeout=300)
def exams():
    active_exams = Exam.query.filter(Exam.is_active == True).all()
    return render_template('exams.html', exams=active_exams)

@exam_bp.route('/exam/<int:exam_id>')
@login_required
def take_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    if not exam.is_active:
        flash('This exam is not currently active.')
        return redirect(url_for('exam.exams'))
    
    user_exam = UserExam.query.filter_by(user_id=current_user.id, exam_id=exam_id).first()
    if user_exam and user_exam.is_completed:
        flash('You have already completed this exam.')
        return redirect(url_for('exam.exam_result', exam_id=exam_id))
    
    if not user_exam:
        user_exam = UserExam(user_id=current_user.id, exam_id=exam_id)
        db.session.add(user_exam)
        db.session.commit()
    
    return render_template('take_exam.html', exam=exam, user_exam=user_exam)

@exam_bp.route('/submit_exam/<int:exam_id>', methods=['POST'])
@login_required
@limiter.limit("1 per minute")
def submit_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    user_exam = UserExam.query.filter_by(user_id=current_user.id, exam_id=exam_id).first_or_404()
    
    if user_exam.is_completed:
        return jsonify({'error': 'Exam already submitted'}), 400
    
    answers = request.json.get('answers')
    if not answers:
        return jsonify({'error': 'No answers provided'}), 400
    
    user_exam.answers = answers
    user_exam.completed_at = datetime.utcnow()
    
    score = calculate_score(exam.questions, answers)
    user_exam.score = score
    
    db.session.commit()
    
    # Award points based on the score
    points_awarded = award_points(current_user, score)
    
    cache.delete(f'user_{current_user.id}_exam_{exam_id}_result')
    
    return jsonify({
        'message': 'Exam submitted successfully',
        'score': score,
        'points_awarded': points_awarded
    }), 200

@exam_bp.route('/exam_result/<int:exam_id>')
@login_required
@cache.cached(timeout=300, key_prefix='user_exam_result')
def exam_result(exam_id):
    user_exam = UserExam.query.filter_by(user_id=current_user.id, exam_id=exam_id).first_or_404()
    exam = user_exam.exam
    
    return render_template('exam_result.html', user_exam=user_exam, exam=exam)