# SSquare Self Study

SSquare Self Study is a comprehensive web application designed to help students prepare for competitive exams like JEE Main and JEE Advanced. The platform offers a variety of features to enhance the learning experience and track progress.

## Features

- User authentication and registration
- Personalized dashboard
- Exam taking and scoring
- Performance analysis
- Study materials
- Progress tracking
- Leaderboards
- Notifications
- Study recommendations
- Question prediction
- AI-powered study recommendations
- Personalized learning paths

## Technologies Used

- Flask (Python web framework)
- SQLAlchemy (ORM)
- Flask-Login (User session management)
- Matplotlib (Data visualization)
- Discord.py (Discord bot integration)
- Tailwind CSS (Styling)
- Scikit-learn (Machine learning for predictions)
- TensorFlow (Deep learning for advanced predictions)
- Natural Language Processing (NLP) libraries

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Likhithsai2580/ssquare-self-study.git
   cd ssquare-self-study
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add the following variables:
     ```
     SECRET_KEY=your_secret_key
     DATABASE_URL=sqlite:///ssquare.db
     DISCORD_BOT_TOKEN=your_discord_bot_token
     DISCORD_GUILD_ID=your_discord_guild_id
     ```

5. Initialize the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Run the application:
   ```
   python run.py
   ```

## Usage

1. Register a new account or log in to an existing one.
2. Explore the dashboard to see upcoming exams and your progress.
3. Take exams and review your results.
4. Study using the provided materials and recommendations.
5. Check the leaderboard to see how you compare to other users.
6. Receive notifications about new exams and your performance.
7. Utilize the prediction feature to get personalized question recommendations.
8. Follow AI-generated study plans tailored to your performance and goals.

## Prediction Feature

The SSquare Self Study platform incorporates advanced machine learning algorithms to provide personalized question predictions and study recommendations:

### Question Prediction

- Uses historical exam data and user performance to predict likely questions in upcoming exams.
- Employs natural language processing to analyze question patterns and trends.
- Continuously improves predictions based on new exam data and user feedback.

### Study Recommendations

- Analyzes individual user performance across different topics and question types.
- Identifies knowledge gaps and areas for improvement.
- Generates personalized study plans focusing on weak areas and reinforcing strengths.

### Adaptive Learning

- Adjusts difficulty and topic focus based on user progress and performance.
- Provides real-time updates to study recommendations as users complete more exams and practice sessions.

## How It Works

1. Data Collection: The system collects data from past exams, user performance, and expert-curated content.
2. Feature Extraction: Relevant features are extracted from questions, answers, and user interactions.
3. Model Training: Machine learning models are trained on this data to recognize patterns and make predictions.
4. Personalization: The trained models are applied to individual user data to generate personalized predictions and recommendations.
5. Continuous Learning: The system updates its models regularly with new data to improve accuracy over time.

## Accuracy and Limitations

While our prediction system strives for high accuracy, it's important to note that it's based on historical data and patterns. The actual exam questions may vary, and users should use the predictions as a study aid rather than a definitive guide.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Project Structure

```
ssquare-self-study/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── static/
│   ├── templates/
│   └── utils/
├── migrations/
├── tests/
├── .env
├── .gitignore
├── config.py
├── requirements.txt
├── run.py
```

## Development

### Setting Up a Development Environment

1. Follow the installation steps mentioned above.
2. Install development dependencies:
   ```
   pip install -r requirements-dev.txt
   ```
3. Set up pre-commit hooks:
   ```
   pre-commit install
   ```

### Running Tests

To run the test suite:

```
pytest
```

### Code Style

We use Black for code formatting and flake8 for linting. To format your code:

```
black .
```

To run the linter:

```
flake8
```

## Deployment

### Heroku Deployment

1. Create a Heroku account and install the Heroku CLI.
2. Login to Heroku:
   ```
   heroku login
   ```
3. Create a new Heroku app:
   ```
   heroku create ssquare-self-study
   ```
4. Set up environment variables:
   ```
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set DATABASE_URL=your_database_url
   heroku config:set DISCORD_BOT_TOKEN=your_discord_bot_token
   heroku config:set DISCORD_GUILD_ID=your_discord_guild_id
   ```
5. Push to Heroku:
   ```
   git push heroku main
   ```
6. Run database migrations:
   ```
   heroku run flask db upgrade
   ```

## Contributing

We welcome contributions to the SSquare Self Study project! Here's how you can contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

Please make sure to update tests as appropriate and adhere to the code style guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Scikit-learn](https://scikit-learn.org/)
- [TensorFlow](https://www.tensorflow.org/)

## Contact

For any questions or concerns, please open an issue on the GitHub repository or contact the maintainers directly.

---

Thank you for using SSquare Self Study! We hope this platform helps you achieve your educational goals.
