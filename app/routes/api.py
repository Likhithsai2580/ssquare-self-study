from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app.models import User, Exam, UserExam
from app import db, limiter

api_bp = Blueprint('api', __name__)

@api_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

@api_bp.route('/protected', methods=['GET'])
@jwt_required
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@api_bp.route('/exams', methods=['GET'])
@jwt_required
def get_exams():
    exams = Exam.query.filter(Exam.is_active == True).all()
    return jsonify([{
        'id': exam.id,
        'title': exam.title,
        'subject': exam.subject,
        'start_time': exam.start_time.isoformat(),
        'end_time': exam.end_time.isoformat()
    } for exam in exams]), 200

@api_bp.route('/submit_exam/<int:exam_id>', methods=['POST'])
@jwt_required
@limiter.limit("1 per minute")
def submit_exam(exam_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    exam = Exam.query.get_or_404(exam_id)
    user_exam = UserExam.query.filter_by(user_id=user.id, exam_id=exam_id).first_or_404()
    
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
    
    return jsonify({
        'message': 'Exam submitted successfully',
        'score': score
    }), 200