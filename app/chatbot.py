from app.perplexica import Perplexica

class Chatbot:
    def __init__(self):
        self.perplexica = Perplexica()

    def get_response(self, user_input):
        # Use Perplexica to generate a response
        search_results = self.perplexica.search(user_input)
        if search_results:
            response = search_results[0]['title']
        else:
            response = "I'm sorry, I couldn't find an answer to your question."
        return response

    def get_personalized_response(self, user_input, user_context):
        # Use Perplexica to generate a response with context-awareness
        search_results = self.perplexica.search(user_input)
        if search_results:
            response = search_results[0]['title']
            # Add personalization based on user context
            if user_context:
                response += f" (Based on your previous interactions: {user_context})"
        else:
            response = "I'm sorry, I couldn't find an answer to your question."
        return response

chatbot = Chatbot()
