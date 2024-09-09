import unittest
from app import create_app, db
from app.models import User, Exam, UserExam, Badge, UserPoints
from app.routes import generate_learning_path, award_points, check_and_award_badges

class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_learning_path(self):
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        exam = Exam(subject='Mathematics', questions=[{'topic': 'Algebra', 'question': 'Test', 'options': ['A', 'B', 'C', 'D'], 'correct_answer': 0}])
        db.session.add(exam)
        db.session.commit()

        user_exam = UserExam(user_id=user.id, exam_id=exam.id, score=80)
        db.session.add(user_exam)
        db.session.commit()

        path = generate_learning_path(user.id, 'Mathematics')
        self.assertIn('Algebra', path['strong_topics'])

    def test_gamification(self):
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        award_points(user, 100)
        self.assertEqual(user.points.points, 100)

        Badge(name='Point Collector', description='Earn 1000 points').save()
        check_and_award_badges(user)
        self.assertEqual(len(user.badges.all()), 0)

        award_points(user, 900)
        check_and_award_badges(user)
        self.assertEqual(len(user.badges.all()), 1)

if __name__ == '__main__':
    unittest.main()