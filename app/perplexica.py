import requests
from bs4 import BeautifulSoup
import random
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Perplexica:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search(self, query):
        url = f"https://www.google.com/search?q={query}"
        response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        
        results = []
        for g in soup.find_all('div', class_='g'):
            anchors = g.find_all('a')
            if anchors:
                link = anchors[0]['href']
                title = g.find('h3', class_='r')
                item = {
                    "title": title.text if title else "",
                    "link": link
                }
                results.append(item)
        
        return results

    def generate_question(self, subject, topic):
        search_query = f"{subject} {topic} exam question"
        search_results = self.search(search_query)
        
        if not search_results:
            return None

        # Use the search results to create a question
        result = random.choice(search_results)
        question = f"Based on the topic '{topic}' in {subject}, {result['title']}"
        options = [
            f"Option related to {result['title']}",
            f"Another option about {topic}",
            f"Third option regarding {subject}",
            f"Fourth option on {topic} in {subject}"
        ]
        correct_answer = random.randint(0, 3)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer
        }

    def generate_question_ml(self, subject, topic):
        search_query = f"{subject} {topic} exam question"
        search_results = self.search(search_query)
        
        if not search_results:
            return None

        # Use TF-IDF and cosine similarity to create a question
        vectorizer = TfidfVectorizer()
        documents = [result['title'] for result in search_results]
        tfidf_matrix = vectorizer.fit_transform(documents)
        query_vector = vectorizer.transform([search_query])
        similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
        
        best_match_index = np.argmax(similarities)
        best_match = search_results[best_match_index]
        
        question = f"Based on the topic '{topic}' in {subject}, {best_match['title']}"
        options = [
            f"Option related to {best_match['title']}",
            f"Another option about {topic}",
            f"Third option regarding {subject}",
            f"Fourth option on {topic} in {subject}"
        ]
        correct_answer = random.randint(0, 3)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer
        }

perplexica = Perplexica()

def generate_questions(subject, num_questions=10):
    topics = [
        "Algebra", "Geometry", "Calculus", "Trigonometry",  # Math topics
        "Mechanics", "Thermodynamics", "Electromagnetism", "Optics",  # Physics topics
        "Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", "Biochemistry"  # Chemistry topics
    ]
    
    questions = []
    for _ in range(num_questions):
        topic = random.choice(topics)
        question = perplexica.generate_question_ml(subject, topic)
        if question:
            questions.append(question)
    
    return questions

def predict_questions(exam_type, subject, num_questions=5):
    predicted_questions = generate_questions(subject, num_questions)
    return predicted_questions
