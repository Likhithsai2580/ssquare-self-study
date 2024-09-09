from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Channel, Exam, UserExam, Result, StudyMaterial, Progress, Notification, PredictedQuestion, StudyGroup, ForumPost, ForumComment, LearningPath, UserPoints, Badge, UserBadge
from werkzeug.urls import url_parse
from datetime import datetime
from sqlalchemy import func
import json
import matplotlib.pyplot as plt
import io
import base64
from app.discord_bot import send_message_to_channel
import asyncio
from flask_sse import sse
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.prediction import predict_questions, get_predictions
from app.exam_utils import get_exam_statistics
from app.perplexica import Perplexica
from app.chatbot import chatbot

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html', title='Home')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        user = User(username=request.form['username'], email=request.form['email'])
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        
        # Create a new channel for the user
        channel = Channel(name=user.username, category='MPC', user_id=user.id)
        db.session.add(channel)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/exams')
@login_required
def exams():
    upcoming_exams = Exam.query.filter(Exam.start_time > datetime.utcnow()).order_by(Exam.start_time).all()
    return render_template('exams.html', title='Upcoming Exams', exams=upcoming_exams)

@main.route('/exam/<int:exam_id>')
@login_required
def take_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    if datetime.utcnow() < exam.start_time:
        flash('This exam has not started yet.')
        return redirect(url_for('main.exams'))
    if datetime.utcnow() > exam.end_time:
        flash('This exam has already ended.')
        return redirect(url_for('main.exams'))
    
    user_exam = UserExam.query.filter_by(user_id=current_user.id, exam_id=exam_id).first()
    if user_exam and user_exam.completed_at:
        flash('You have already completed this exam.')
        return redirect(url_for('main.exams'))
    
    if not user_exam:
        user_exam = UserExam(user_id=current_user.id, exam_id=exam_id)
        db.session.add(user_exam)
        db.session.commit()
    
    return render_template('take_exam.html', title='Take Exam', exam=exam, user_exam=user_exam)

@main.route('/submit_exam/<int:exam_id>', methods=['POST'])
@login_required
def submit_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    user_exam = UserExam.query.filter_by(user_id=current_user.id, exam_id=exam_id).first_or_404()
    
    if user_exam.completed_at:
        return jsonify({'error': 'Exam already submitted'}), 400
    
    answers = request.json.get('answers')
    if not answers:
        return jsonify({'error': 'No answers provided'}), 400
    
    user_exam.answers = answers
    user_exam.completed_at = datetime.utcnow()
    
    # Calculate score
    score = 0
    for i, question in enumerate(exam.questions):
        if answers.get(str(i)) == question['correct_answer']:
            score += 1
    user_exam.score = (score / len(exam.questions)) * 100
    
    # Update progress
    progress = Progress.query.filter_by(user_id=current_user.id, subject=exam.subject).first()
    if not progress:
        progress = Progress(user_id=current_user.id, subject=exam.subject)
        db.session.add(progress)
    
    progress.total_questions += len(exam.questions)
    progress.correct_answers += score
    db.session.commit()

    # Create a Result object
    result = Result(user_id=current_user.id, exam_id=exam_id, score=user_exam.score)
    db.session.add(result)
    db.session.commit()
    
    # Send result to user's channel
    send_result_to_channel(current_user, result)
    
    # Send notification about exam result
    send_notification(current_user.id, f"Your {exam.subject} exam result: {user_exam.score:.2f}%")
    
    # Award points based on score
    points_to_award = int(user_exam.score)
    award_points(current_user, points_to_award)
    
    # Check and award badges
    new_badges = check_and_award_badges(current_user)
    
    return jsonify({
        'message': 'Exam submitted successfully',
        'score': user_exam.score,
        'points_earned': points_to_award,
        'new_badges': [badge.name for badge in new_badges]
    }), 200

def send_result_to_channel(user, result):
    channel_name = f"{user.username.lower()}-results"
    message = f"New exam result for {user.username}: Exam {result.exam_id}, Score: {result.score:.2f}%"
    asyncio.run(send_message_to_channel(channel_name, message))

@main.route('/dashboard')
@login_required
def dashboard():
    user_exams = UserExam.query.filter_by(user_id=current_user.id).order_by(UserExam.completed_at.desc()).all()
    exam_stats = get_exam_statistics()
    return render_template('dashboard.html', title='Dashboard', user_exams=user_exams, exam_stats=exam_stats)

@main.route('/exam_result/<int:exam_id>')
@login_required
def exam_result(exam_id):
    user_exam = UserExam.query.filter_by(user_id=current_user.id, exam_id=exam_id).first_or_404()
    exam = Exam.query.get_or_404(exam_id)
    
    # Generate performance graph
    correct_answers = sum(1 for i, q in enumerate(exam.questions) if user_exam.answers.get(str(i)) == q['correct_answer'])
    incorrect_answers = len(exam.questions) - correct_answers
    
    plt.figure(figsize=(8, 6))
    plt.pie([correct_answers, incorrect_answers], labels=['Correct', 'Incorrect'], autopct='%1.1f%%')
    plt.title('Exam Performance')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return render_template('exam_result.html', title='Exam Result', user_exam=user_exam, exam=exam, graph_url=graph_url)

@main.route('/performance_analysis')
@login_required
def performance_analysis():
    user_exams = UserExam.query.filter_by(user_id=current_user.id).order_by(UserExam.completed_at).all()
    exam_scores = [ue.score for ue in user_exams if ue.score is not None]
    
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(exam_scores) + 1), exam_scores, marker='o')
    plt.title('Performance Over Time')
    plt.xlabel('Exam Number')
    plt.ylabel('Score (%)')
    plt.ylim(0, 100)
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    # Calculate additional statistics
    avg_score = sum(exam_scores) / len(exam_scores) if exam_scores else 0
    best_score = max(exam_scores) if exam_scores else 0
    worst_score = min(exam_scores) if exam_scores else 0
    total_exams = len(exam_scores)
    
    # Calculate subject-wise performance
    subject_performance = db.session.query(
        Exam.subject,
        func.avg(UserExam.score).label('avg_score'),
        func.count(UserExam.id).label('exam_count')
    ).join(UserExam).filter(UserExam.user_id == current_user.id).group_by(Exam.subject).all()
    
    # Calculate performance by topic
    topic_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
    for user_exam in user_exams:
        exam = user_exam.exam
        for i, question in enumerate(exam.questions):
            topic = question.get('topic', 'General')
            topic_performance[topic]['total'] += 1
            if user_exam.answers.get(str(i)) == question['correct_answer']:
                topic_performance[topic]['correct'] += 1
    
    for topic in topic_performance:
        topic_performance[topic]['percentage'] = (topic_performance[topic]['correct'] / topic_performance[topic]['total']) * 100
    
    # Calculate improvement over time
    if len(exam_scores) > 1:
        improvement = exam_scores[-1] - exam_scores[0]
        improvement_percentage = (improvement / exam_scores[0]) * 100 if exam_scores[0] != 0 else 0
    else:
        improvement = 0
        improvement_percentage = 0
    
    return render_template('performance_analysis.html', title='Performance Analysis', 
                           graph_url=graph_url, avg_score=avg_score, best_score=best_score, 
                           worst_score=worst_score, total_exams=total_exams, 
                           subject_performance=subject_performance,
                           topic_performance=dict(topic_performance),
                           improvement=improvement,
                           improvement_percentage=improvement_percentage)

@main.route('/study_materials')
@login_required
def study_materials():
    materials = StudyMaterial.query.order_by(StudyMaterial.subject, StudyMaterial.title).all()
    return render_template('study_materials.html', title='Study Materials', materials=materials)

@main.route('/study_material/<int:material_id>')
@login_required
def study_material(material_id):
    material = StudyMaterial.query.get_or_404(material_id)
    return render_template('study_material.html', title=material.title, material=material)

@main.route('/progress')
@login_required
def view_progress():
    progress = Progress.query.filter_by(user_id=current_user.id).all()
    return render_template('progress.html', title='Your Progress', progress=progress)

@main.route('/leaderboard')
@login_required
def leaderboard():
    top_users = db.session.query(User, UserPoints.points).join(UserPoints).order_by(UserPoints.points.desc()).limit(10).all()
    return render_template('leaderboard.html', title='Leaderboard', top_users=top_users)

@main.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id, read=False).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', title='Notifications', notifications=notifications)

@main.route('/mark_notification_read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == current_user.id:
        notification.read = True
        db.session.commit()
    return redirect(url_for('main.notifications'))

def send_notification(user_id, message):
    notification = Notification(user_id=user_id, message=message)
    db.session.add(notification)
    db.session.commit()
    sse.publish({"message": message}, type='notification', channel=f'user_{user_id}')

@main.route('/study_recommendations')
@login_required
def study_recommendations():
    # Get user's exam history
    user_exams = UserExam.query.filter_by(user_id=current_user.id).all()
    
    # Calculate topic performance
    topic_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
    for user_exam in user_exams:
        exam = user_exam.exam
        for i, question in enumerate(exam.questions):
            topic = question.get('topic', 'General')
            topic_performance[topic]['total'] += 1
            if user_exam.answers.get(str(i)) == question['correct_answer']:
                topic_performance[topic]['correct'] += 1
    
    for topic in topic_performance:
        topic_performance[topic]['percentage'] = (topic_performance[topic]['correct'] / topic_performance[topic]['total']) * 100
    
    # Identify weak topics (below 70% performance)
    weak_topics = [topic for topic, perf in topic_performance.items() if perf['percentage'] < 70]
    
    # Use local Perplexica implementation to get study recommendations
    recommended_materials = []
    for topic in weak_topics:
        materials = StudyMaterial.query.filter_by(topic=topic).all()
        if not materials:
            # If no materials found in the database, generate some using Perplexica
            perplexica = Perplexica()
            search_results = perplexica.search(f"{topic} study material")
            materials = [{'title': result['title'], 'link': result['link']} for result in search_results[:3]]
        
        recommended_materials.append({
            'topic': topic,
            'materials': materials
        })
    
    return render_template('study_recommendations.html', title='Study Recommendations',
                           topic_performance=dict(topic_performance),
                           recommended_materials=recommended_materials)

@main.route('/predict_questions', methods=['GET', 'POST'])
@login_required
def predict_questions_route():
    if request.method == 'POST':
        exam_type = request.form['exam_type']
        subject = request.form['subject']
        predicted_questions = predict_questions(exam_type, subject)
        if predicted_questions:
            flash('New questions predicted successfully!', 'success')
        else:
            flash('Failed to predict new questions. Please try again later.', 'error')
        return redirect(url_for('main.view_predictions', exam_type=exam_type, subject=subject))
    return render_template('predict_questions.html', title='Predict Questions')

@main.route('/view_predictions/<exam_type>/<subject>')
@login_required
def view_predictions(exam_type, subject):
    predictions = get_predictions(exam_type, subject)
    return render_template('view_predictions.html', title='View Predictions', predictions=predictions, exam_type=exam_type, subject=subject)

@main.route('/study_groups')
@login_required
def study_groups():
    groups = StudyGroup.query.all()
    return render_template('study_groups.html', title='Study Groups', groups=groups)

@main.route('/create_study_group', methods=['GET', 'POST'])
@login_required
def create_study_group():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        new_group = StudyGroup(name=name, description=description, creator=current_user)
        new_group.members.append(current_user)
        db.session.add(new_group)
        db.session.commit()
        flash('Study group created successfully!', 'success')
        return redirect(url_for('main.study_groups'))
    return render_template('create_study_group.html', title='Create Study Group')

@main.route('/study_group/<int:group_id>')
@login_required
def study_group(group_id):
    group = StudyGroup.query.get_or_404(group_id)
    return render_template('study_group.html', title=group.name, group=group)

@main.route('/join_study_group/<int:group_id>')
@login_required
def join_study_group(group_id):
    group = StudyGroup.query.get_or_404(group_id)
    if current_user not in group.members:
        group.members.append(current_user)
        db.session.commit()
        flash('You have joined the study group!', 'success')
    else:
        flash('You are already a member of this group.', 'info')
    return redirect(url_for('main.study_group', group_id=group_id))

@main.route('/forum')
@login_required
def forum():
    posts = ForumPost.query.order_by(ForumPost.created_at.desc()).all()
    return render_template('forum.html', title='Discussion Forum', posts=posts)

@main.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = ForumPost(title=title, content=content, user=current_user)
        db.session.add(new_post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.forum'))
    return render_template('create_post.html', title='Create Post')

@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    if request.method == 'POST':
        content = request.form['content']
        new_comment = ForumComment(content=content, user=current_user, post=post)
        db.session.add(new_comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('main.post', post_id=post_id))
    return render_template('post.html', title=post.title, post=post)

def generate_learning_path(user_id, subject):
    user_exams = UserExam.query.filter_by(user_id=user_id).join(Exam).filter(Exam.subject == subject).all()
    topic_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
    
    for user_exam in user_exams:
        for i, question in enumerate(user_exam.exam.questions):
            topic = question.get('topic', 'General')
            topic_performance[topic]['total'] += 1
            if user_exam.answers.get(str(i)) == question['correct_answer']:
                topic_performance[topic]['correct'] += 1
    
    for topic in topic_performance:
        topic_performance[topic]['percentage'] = (topic_performance[topic]['correct'] / topic_performance[topic]['total']) * 100
    
    weak_topics = [topic for topic, perf in topic_performance.items() if perf['percentage'] < 70]
    strong_topics = [topic for topic, perf in topic_performance.items() if perf['percentage'] >= 70]
    
    learning_path = {
        'weak_topics': weak_topics,
        'strong_topics': strong_topics,
        'recommended_order': weak_topics + strong_topics
    }
    
    return learning_path

@main.route('/learning_path/<subject>')
@login_required
def learning_path(subject):
    existing_path = LearningPath.query.filter_by(user_id=current_user.id, subject=subject).first()
    
    if existing_path:
        path = existing_path.topics
    else:
        path = generate_learning_path(current_user.id, subject)
        new_path = LearningPath(user_id=current_user.id, subject=subject, topics=path)
        db.session.add(new_path)
        db.session.commit()
    
    return render_template('learning_path.html', title=f'{subject} Learning Path', subject=subject, path=path)

def award_points(user, points):
    if not user.points:
        user.points = UserPoints(user_id=user.id)
    user.points.points += points
    user.points.last_updated = datetime.utcnow()
    db.session.commit()

def check_and_award_badges(user):
    total_exams = UserExam.query.filter_by(user_id=user.id).count()
    total_points = user.points.points if user.points else 0
    
    badges_to_award = []
    
    if total_exams >= 5 and not user.badges.filter_by(name='Exam Master').first():
        exam_master_badge = Badge.query.filter_by(name='Exam Master').first()
        badges_to_award.append(exam_master_badge)
    
    if total_points >= 1000 and not user.badges.filter_by(name='Point Collector').first():
        point_collector_badge = Badge.query.filter_by(name='Point Collector').first()
        badges_to_award.append(point_collector_badge)
    
    for badge in badges_to_award:
        user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
        db.session.add(user_badge)
    
    db.session.commit()
    return badges_to_award

@main.route('/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot_view():
    if request.method == 'POST':
        user_input = request.form['user_input']
        response = chatbot.get_response(user_input)
        return jsonify({'response': response})
    return render_template('chatbot.html', title='AI Chatbot')