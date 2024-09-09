from app import create_app, db
from app.exam_utils import schedule_exams
from app.discord_bot import start_discord_bot
from app.routes import create_sample_study_materials
from app.create_badges import create_initial_badges
import threading

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_study_materials()
        create_initial_badges()
    
    # Start the exam scheduling in a separate thread
    scheduler_thread = threading.Thread(target=schedule_exams)
    scheduler_thread.start()
    
    # Start the Discord bot in a separate thread
    discord_thread = threading.Thread(target=start_discord_bot)
    discord_thread.start()
    
    app.run(debug=True)