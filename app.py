# app.py

"""Main Flask application for LearningAI.
Provides routes for signup, login, dashboard, semester view, quiz handling, and recommendations.
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_PATH = os.path.join(os.path.dirname(__file__), "learning_ai.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Authentication ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        branch = request.form['branch']
        semester = int(request.form['semester'])
        pw_hash = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (name, email, password_hash, branch, semester) VALUES (?,?,?,?,?)",
                (name, email, pw_hash, branch, semester)
            )
            conn.commit()
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['branch'] = user['branch']
            session['semester'] = user['semester']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------- Dashboard ----------
@app.route('/')
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db_connection()
    # Get subjects for current branch & semester
    subjects = conn.execute(
        "SELECT * FROM subjects WHERE branch = ? AND semester = ?",
        (session['branch'], session['semester'])
    ).fetchall()
    # Get quiz scores for this user
    scores = conn.execute(
        "SELECT s.name, q.score FROM quizzes q JOIN subjects s ON q.subject_id = s.id WHERE q.user_id = ?",
        (user_id,)
    ).fetchall()
    conn.close()
    
    # Load Domain Roadmap
    roadmap_path = os.path.join(os.path.dirname(__file__), 'data', 'domain_roadmaps.json')
    domain_roadmap = []
    if os.path.exists(roadmap_path):
        import json
        with open(roadmap_path, 'r') as f:
            all_roadmaps = json.load(f)
            domain_roadmap = all_roadmaps.get(session['branch'], [])

    # Build a dict of subject -> score (or None)
    score_map = {row['name']: row['score'] for row in scores}
    return render_template('dashboard.html', name=session['name'], branch=session['branch'], semester=session['semester'], subjects=subjects, scores=score_map, domain_roadmap=domain_roadmap)

# ---------- Semester view ----------
@app.route('/semester/<int:sem>')
def semester_view(sem):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM subjects WHERE branch = ? AND semester = ?",
        (session['branch'], sem)
    ).fetchall()
    conn.close()

    # Parse roadmap_json for each subject
    subjects = []
    for row in rows:
        s = dict(row)
        try:
            s['roadmap'] = json.loads(s['roadmap_json'])
        except (TypeError, ValueError):
            s['roadmap'] = []
        subjects.append(s)

    return render_template('semester.html', semester=sem, subjects=subjects)

# ---------- Quiz ----------
@app.route('/quiz/<int:subject_id>', methods=['GET', 'POST'])
def quiz(subject_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    subject = conn.execute('SELECT * FROM subjects WHERE id = ?', (subject_id,)).fetchone()
    
    if request.method == 'POST':
        # Backend-controlled Grading Logic
        # Correct answer key (corresponding to the mock quiz in quiz.html)
        # In a real app, this would be fetched from a 'questions' table
        answer_key = {
            'q1': 'correct',
            'q2': 'correct',
            'q3': 'correct',
            'q4': 'correct',
            'q5': 'correct'
        }
        
        score_counter = 0
        total_questions = len(answer_key)
        
        for q_id, correct_val in answer_key.items():
            user_answer = request.form.get(q_id)
            if user_answer == correct_val:
                score_counter += 1
        
        # Calculate percentage
        final_score = int((score_counter / total_questions) * 100)
        
        # Store in DB
        conn.execute(
            "INSERT INTO quizzes (user_id, subject_id, score) VALUES (?,?,?)",
            (session['user_id'], subject_id, final_score)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
        
    conn.close()
    return render_template('quiz.html', subject=subject)

# ---------- Recommendations ----------
@app.route('/recommendations')
def recommendations():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    from recommender import get_recommendations
    recs = get_recommendations(session['user_id'])
    return render_template('recommendations.html', recommendations=recs)

# ---------- Update Profile ----------
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    new_branch = request.form['branch']
    new_sem = int(request.form['semester'])
    
    conn = get_db_connection()
    conn.execute(
        "UPDATE users SET branch = ?, semester = ? WHERE id = ?",
        (new_branch, new_sem, session['user_id'])
    )
    conn.commit()
    conn.close()
    
    # Update session
    session['branch'] = new_branch
    session['semester'] = new_sem
    
    return redirect(url_for('dashboard'))

# ---------- Global Library ----------
@app.route('/library', methods=['GET', 'POST'])
def library():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    selected_branch = request.form.get('branch') or request.args.get('branch') or session['branch']
    # If using POST/GET form, 'semester' might be string; usually safe to cast
    try:
        selected_sem = int(request.form.get('semester') or request.args.get('semester') or session['semester'])
    except:
        selected_sem = 1
        
    conn = get_db_connection()
    
    # Get subjects
    subjects = conn.execute(
        "SELECT id, name, branch, semester FROM subjects WHERE branch = ? AND semester = ?",
        (selected_branch, selected_sem)
    ).fetchall()
    
    # For each subject, get resources
    library_data = []
    for sub in subjects:
        res = conn.execute(
            "SELECT note_url, video_url FROM resources WHERE subject_id = ?",
            (sub['id'],)
        ).fetchall()
        
        library_data.append({
            "name": sub['name'],
            "notes": [r['note_url'] for r in res],
            "videos": [r['video_url'] for r in res]
        })
        
    conn.close()
    
    # Pass branch list for dropdown
    branches = [
        "Computer Science Engineering", "Information Technology", "Artificial Intelligence & Machine Learning",
        "Data Science", "Web Development", "Cyber Security", "Cloud & DevOps",
        "Mechanical Engineering", "Electrical Engineering", "Electronics & Communication Engineering",
        "Civil Engineering", "Chemical Engineering", "Biotechnology",
        "Automobile Engineering", "Aerospace Engineering", "Instrumentation Engineering"
    ]
    
    return render_template('library.html', 
                           library_data=library_data, 
                           current_branch=selected_branch, 
                           current_sem=selected_sem,
                           branches=branches)

# ---------- Resource Viewer ----------
@app.route('/view_resource')
def view_resource():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    res_type = request.args.get('type') # 'notes' or 'video'
    subject_name = request.args.get('subject')
    branch = request.args.get('branch') or session['branch']
    try:
        semester = int(request.args.get('semester') or session['semester'])
    except:
        semester = session['semester']
    
    conn = get_db_connection()
    row = conn.execute(
        """
        SELECT r.note_url, r.video_url 
        FROM resources r
        JOIN subjects s ON r.subject_id = s.id
        WHERE s.name = ? AND s.branch = ? AND s.semester = ?
        """,
        (subject_name, branch, semester)
    ).fetchone()
    conn.close()

    if not row:
        # Fallback to a search if not found in our seed data
        if res_type == 'video':
            embed_url = f"https://www.youtube.com/embed?listType=search&list={subject_name}+tutorial"
        else:
            embed_url = f"https://www.bing.com/search?q={subject_name}+notes+pdf"
    else:
        embed_url = row['video_url'] if res_type == 'video' else row['note_url']

    return render_template('viewer.html', subject=subject_name, res_type=res_type, embed_url=embed_url)

if __name__ == '__main__':
    # Ensure DB exists
    if not os.path.exists(DB_PATH):
        from db_init import init_db
        init_db()
    app.run(host="0.0.0.0", port=5000)
