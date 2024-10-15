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