import random
from app import db
from app.models import User, Badge, Notification

def calculate_score(questions, answers):
    correct_answers = sum(1 for q, a in zip(questions, answers.values()) if q['correct_answer'] == a)
    return (correct_answers / len(questions)) * 100

def award_points(user, score):
    points_awarded = int(score)
    user.points += points_awarded
    db.session.commit()
    check_and_award_badges(user)
    return points_awarded

def check_and_award_badges(user):
    # Example badge criteria
    if user.points >= 1000 and not user.badges.filter_by(name='Point Collector').first():
        badge = Badge.query.filter_by(name='Point Collector').first()
        user.badges.append(badge)
        create_notification(user, f"You've earned the '{badge.name}' badge!")
    
    if len(user.user_exams) >= 5 and not user.badges.filter_by(name='Exam Master').first():
        badge = Badge.query.filter_by(name='Exam Master').first()
        user.badges.append(badge)
        create_notification(user, f"You've earned the '{badge.name}' badge!")
    
    # Additional badge criteria
    if user.points >= 5000 and not user.badges.filter_by(name='Superstar').first():
        badge = Badge.query.filter_by(name='Superstar').first()
        user.badges.append(badge)
        create_notification(user, f"You've earned the '{badge.name}' badge!")
    
    if len(user.user_exams) >= 10 and not user.badges.filter_by(name='Exam Pro').first():
        badge = Badge.query.filter_by(name='Exam Pro').first()
        user.badges.append(badge)
        create_notification(user, f"You've earned the '{badge.name}' badge!")
    
    db.session.commit()

def create_notification(user, message):
    notification = Notification(user_id=user.id, message=message)
    db.session.add(notification)
    db.session.commit()

def generate_learning_path(user_id, subject):
    user_exams = UserExam.query.filter_by(user_id=user_id).join(Exam).filter(Exam.subject == subject).all()
    
    topic_performance = {}
    for user_exam in user_exams:
        for i, question in enumerate(user_exam.exam.questions):
            topic = question['topic']
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0}
            topic_performance[topic]['total'] += 1
            if user_exam.answers.get(str(i)) == question['correct_answer']:
                topic_performance[topic]['correct'] += 1
    
    for topic in topic_performance:
        topic_performance[topic]['percentage'] = (topic_performance[topic]['correct'] / topic_performance[topic]['total']) * 100
    
    weak_topics = [topic for topic, data in topic_performance.items() if data['percentage'] < 70]
    strong_topics = [topic for topic, data in topic_performance.items() if data['percentage'] >= 70]
    
    recommended_order = weak_topics + strong_topics
    random.shuffle(recommended_order)
    
    return {
        'recommended_order': recommended_order,
        'weak_topics': weak_topics,
        'strong_topics': strong_topics
    }

def analyze_performance(user_id):
    user_exams = UserExam.query.filter_by(user_id=user_id).all()
    
    performance_data = {
        'total_exams': len(user_exams),
        'average_score': sum(exam.score for exam in user_exams) / len(user_exams) if user_exams else 0,
        'best_score': max(exam.score for exam in user_exams) if user_exams else 0,
        'worst_score': min(exam.score for exam in user_exams) if user_exams else 0,
        'improvement': 0,
        'improvement_percentage': 0
    }
    
    if user_exams:
        first_exam_score = user_exams[0].score
        last_exam_score = user_exams[-1].score
        performance_data['improvement'] = last_exam_score - first_exam_score
        performance_data['improvement_percentage'] = (performance_data['improvement'] / first_exam_score) * 100 if first_exam_score else 0
    
    return performance_data

def generate_detailed_learning_path(user_id, subject):
    learning_path = generate_learning_path(user_id, subject)
    
    # Add more detailed insights
    learning_path['detailed_insights'] = {
        'total_exams': len(learning_path['recommended_order']),
        'weak_topics_count': len(learning_path['weak_topics']),
        'strong_topics_count': len(learning_path['strong_topics'])
    }
    
    return learning_path
