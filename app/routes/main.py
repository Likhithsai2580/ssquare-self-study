from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.analytics import track_page_view
from app.recommendation import get_recommendations

main = Blueprint('main', __name__)

# ... existing routes ...

@main.route('/study_recommendations')
@login_required
def study_recommendations():
    recommendations = get_recommendations(current_user.id, 'Mathematics')  # You can change the subject as needed
    return render_template('study_recommendations.html', recommendations=recommendations)