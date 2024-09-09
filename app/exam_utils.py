import json
from datetime import datetime, timedelta
from app import db
from app.models import Exam, StudyMaterial, User, Notification
from app.perplexica import generate_questions
import schedule
import time
import random
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

def create_exam():
    subjects = ['Mathematics', 'Physics', 'Chemistry']
    subject = random.choice(subjects)
    questions = generate_questions(subject)
    
    start_time = datetime.now().replace(hour=20, minute=0, second=0, microsecond=0) + timedelta(days=1)
    end_time = start_time + timedelta(hours=3)
    
    try:
        new_exam = Exam(subject=subject, questions=questions, start_time=start_time, end_time=end_time)
        db.session.add(new_exam)
        db.session.commit()
        
        # Notify users about the new exam
        notify_users_about_exam(new_exam)
        
        current_app.logger.info(f"New {subject} exam created for {start_time.date()}")
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating exam: {str(e)}")

def notify_users_about_exam(exam):
    users = User.query.all()
    for user in users:
        notification = Notification(
            user_id=user.id,
            message=f"New {exam.subject} exam scheduled for {exam.start_time.strftime('%Y-%m-%d %H:%M')}",
            read=False
        )
        db.session.add(notification)
    db.session.commit()

def schedule_exams():
    schedule.every().day.at("00:01").do(create_exam)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def create_sample_study_materials():
    sample_materials = [
        {
            'title': 'Introduction to Algebra',
            'subject': 'Mathematics',
            'topic': 'Algebra',
            'content': '<h2>What is Algebra?</h2><p>Algebra is a branch of mathematics dealing with symbols and the rules for manipulating those symbols. It is a unifying thread of almost all of mathematics.</p><h3>Basic Concepts:</h3><ul><li>Variables</li><li>Expressions</li><li>Equations</li></ul>'
        },
        # ... (keep other sample materials)
    ]

    try:
        for material in sample_materials:
            existing_material = StudyMaterial.query.filter_by(title=material['title']).first()
            if not existing_material:
                new_material = StudyMaterial(title=material['title'], subject=material['subject'], topic=material['topic'], content=material['content'])
                db.session.add(new_material)
        
        db.session.commit()
        current_app.logger.info("Sample study materials created successfully.")
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating sample study materials: {str(e)}")

def get_exam_statistics():
    total_exams = Exam.query.count()
    exams_by_subject = db.session.query(Exam.subject, db.func.count(Exam.id)).group_by(Exam.subject).all()
    return {
        'total_exams': total_exams,
        'exams_by_subject': dict(exams_by_subject)
    }