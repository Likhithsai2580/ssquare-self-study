from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models import StudyMaterial, UserExam

def get_recommendations(user_id, subject):
    # Get user's exam history
    user_exams = UserExam.query.filter_by(user_id=user_id).all()
    
    # Get all study materials for the subject
    study_materials = StudyMaterial.query.filter_by(subject=subject).all()
    
    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    
    # Fit and transform the study material content
    content_matrix = vectorizer.fit_transform([material.content for material in study_materials])
    
    # Create a user profile based on their exam performance
    user_profile = [0] * len(vectorizer.get_feature_names())
    for exam in user_exams:
        for question in exam.exam.questions:
            if question['subject'] == subject:
                words = vectorizer.build_analyzer()(question['question'])
                for word in words:
                    if word in vectorizer.vocabulary_:
                        user_profile[vectorizer.vocabulary_[word]] += 1
    
    # Calculate similarity between user profile and study materials
    user_vector = vectorizer.transform([' '.join([word for word, count in zip(vectorizer.get_feature_names(), user_profile) for _ in range(count)])])
    similarities = cosine_similarity(user_vector, content_matrix).flatten()
    
    # Sort study materials by similarity
    recommended_materials = sorted(zip(similarities, study_materials), key=lambda x: x[0], reverse=True)
    
    return [material for _, material in recommended_materials[:5]]  # Return top 5 recommendations