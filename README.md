# LearningAI

**LearningAI** is an AI-powered personalized learning recommendation system for engineering students. It guides students through their semesters, evaluates their understanding via subject-wise quizzes (backend-graded), and provides AI-driven recommendations (notes & videos) for weak areas.

## Features
- **Student Dashboard**: View all subjects for your specific Branch and Semester.
- **Roadmaps**: Step-by-step learning paths for every subject.
- **Quiz System**: Multiple-choice quizzes with secure backend grading.
- **AI Recommendations**: Automatic suggestion of resources for subjects with scores < 40%.
- **Premium UI**: Modern dark-mode interface with glassmorphism effects.

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**
   (This will create `learning_ai.db` and seed it with data for 16 branches)
   ```bash
   python db_init.py
   ```

3. **Run the Application**
   ```bash
   python app.py
   ```
   Access the app at: https://ai-based-learning-recommendation-system.onrender.com

## Tech Stack
- **Backend**: Python (Flask)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript (No frameworks, pure Vanilla)
- **AI Logic**: Rule-based scoring engine (Backend-controlled)

## Project Structure
- `app.py`: Main application controller.
- `recommender.py`: AI logic for recommendations.
- `db_init.py`: Database setup and seeding script.
- `generate_data.py`: Utility to generate comprehensive JSON seed data.
- `templates/`: HTML pages (Dashboard, Quiz, Semester, etc.).
- `static/`: CSS and JS assets.

