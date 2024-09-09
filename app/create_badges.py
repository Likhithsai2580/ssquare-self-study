from app import create_app, db
from app.models import Badge

def create_initial_badges():
    badges = [
        {
            'name': 'Exam Master',
            'description': 'Complete 5 exams',
            'image_url': '/static/images/badges/exam_master.png'
        },
        {
            'name': 'Point Collector',
            'description': 'Earn 1000 points',
            'image_url': '/static/images/badges/point_collector.png'
        },
        {
            'name': 'Study Group Leader',
            'description': 'Create a study group with 5 members',
            'image_url': '/static/images/badges/study_group_leader.png'
        },
        {
            'name': 'Forum Contributor',
            'description': 'Make 10 forum posts',
            'image_url': '/static/images/badges/forum_contributor.png'
        }
    ]

    for badge_data in badges:
        badge = Badge.query.filter_by(name=badge_data['name']).first()
        if not badge:
            new_badge = Badge(**badge_data)
            db.session.add(new_badge)
    
    db.session.commit()
    print("Initial badges created successfully.")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        create_initial_badges()