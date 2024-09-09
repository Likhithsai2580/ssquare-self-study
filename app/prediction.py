from app import db
from app.models import Exam, PredictedQuestion
from app.perplexica import predict_questions as perplexica_predict_questions
import json

def get_past_questions(exam_type, subject, limit=100):
    past_exams = Exam.query.filter_by(subject=subject).order_by(Exam.start_time.desc()).limit(limit).all()
    past_questions = []
    for exam in past_exams:
        past_questions.extend(exam.questions)
    return past_questions

def predict_questions(exam_type, subject):
    predicted_questions = perplexica_predict_questions(exam_type, subject)
    
    # Save predicted questions to the database
    for question in predicted_questions:
        new_prediction = PredictedQuestion(
            exam_type=exam_type,
            subject=subject,
            question=question['question'],
            options=json.dumps(question['options']),
            correct_answer=question['correct_answer']
        )
        db.session.add(new_prediction)
    db.session.commit()

    return predicted_questions

def get_predictions(exam_type, subject):
    predictions = PredictedQuestion.query.filter_by(exam_type=exam_type, subject=subject).order_by(PredictedQuestion.created_at.desc()).limit(5).all()
    return [
        {
            'question': pred.question,
            'options': json.loads(pred.options),
            'correct_answer': pred.correct_answer
        } for pred in predictions
    ]