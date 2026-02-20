"""
Career Path Builder - Full Flask Application
Install required packages:
pip install flask flask-login werkzeug python-dotenv

For email functionality, also install:
pip install secure-smtplib
"""

# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database simulation (In production, use SQLite or PostgreSQL)
USERS_FILE = 'users.json'
PROGRESS_FILE = 'progress.json'

# Career roadmaps database
CAREER_ROADMAPS = {
    'web_developer': {
        'title': 'Web Developer',
        'description': 'Full-stack web development path',
        'skills': [
            {'name': 'HTML', 'level': 'Beginner', 'duration': '2 weeks', 'resources': ['MDN Web Docs', 'freeCodeCamp']},
            {'name': 'CSS', 'level': 'Beginner', 'duration': '3 weeks', 'resources': ['CSS Tricks', 'Flexbox Froggy']},
            {'name': 'JavaScript', 'level': 'Intermediate', 'duration': '8 weeks', 'resources': ['JavaScript.info', 'Eloquent JavaScript']},
            {'name': 'Git & GitHub', 'level': 'Beginner', 'duration': '1 week', 'resources': ['Git Documentation', 'GitHub Learning Lab']},
            {'name': 'React', 'level': 'Advanced', 'duration': '6 weeks', 'resources': ['React Docs', 'Full Stack Open']},
            {'name': 'Node.js', 'level': 'Intermediate', 'duration': '4 weeks', 'resources': ['Node.js Docs', 'NodeSchool']},
            {'name': 'Database (SQL/MongoDB)', 'level': 'Intermediate', 'duration': '3 weeks', 'resources': ['PostgreSQL Tutorial', 'MongoDB University']},
            {'name': 'Build Projects', 'level': 'Advanced', 'duration': 'Ongoing', 'resources': ['GitHub', 'Portfolio Projects']}
        ]
    },
    'data_scientist': {
        'title': 'Data Scientist',
        'description': 'Data science and machine learning path',
        'skills': [
            {'name': 'Python Basics', 'level': 'Beginner', 'duration': '3 weeks', 'resources': ['Python.org', 'Codecademy']},
            {'name': 'Statistics & Math', 'level': 'Intermediate', 'duration': '6 weeks', 'resources': ['Khan Academy', 'StatQuest']},
            {'name': 'NumPy & Pandas', 'level': 'Intermediate', 'duration': '4 weeks', 'resources': ['Pandas Docs', 'DataCamp']},
            {'name': 'Data Visualization', 'level': 'Intermediate', 'duration': '2 weeks', 'resources': ['Matplotlib', 'Seaborn', 'Plotly']},
            {'name': 'Machine Learning', 'level': 'Advanced', 'duration': '8 weeks', 'resources': ['Scikit-learn', 'Coursera ML']},
            {'name': 'Deep Learning', 'level': 'Advanced', 'duration': '6 weeks', 'resources': ['TensorFlow', 'PyTorch', 'Fast.ai']},
            {'name': 'SQL & Databases', 'level': 'Intermediate', 'duration': '3 weeks', 'resources': ['Mode Analytics', 'SQLZoo']},
            {'name': 'Build Portfolio Projects', 'level': 'Advanced', 'duration': 'Ongoing', 'resources': ['Kaggle', 'GitHub']}
        ]
    },
    'mobile_developer': {
        'title': 'Mobile App Developer',
        'description': 'iOS and Android development path',
        'skills': [
            {'name': 'Programming Fundamentals', 'level': 'Beginner', 'duration': '3 weeks', 'resources': ['Codecademy', 'SoloLearn']},
            {'name': 'Java/Kotlin (Android)', 'level': 'Intermediate', 'duration': '6 weeks', 'resources': ['Android Developers', 'Udacity']},
            {'name': 'Swift (iOS)', 'level': 'Intermediate', 'duration': '6 weeks', 'resources': ['Swift.org', 'Hacking with Swift']},
            {'name': 'React Native/Flutter', 'level': 'Advanced', 'duration': '5 weeks', 'resources': ['React Native Docs', 'Flutter Docs']},
            {'name': 'UI/UX Design Basics', 'level': 'Beginner', 'duration': '2 weeks', 'resources': ['Material Design', 'Human Interface Guidelines']},
            {'name': 'API Integration', 'level': 'Intermediate', 'duration': '3 weeks', 'resources': ['RESTful APIs', 'GraphQL']},
            {'name': 'App Publishing', 'level': 'Intermediate', 'duration': '1 week', 'resources': ['Google Play Console', 'App Store Connect']},
            {'name': 'Build Portfolio Apps', 'level': 'Advanced', 'duration': 'Ongoing', 'resources': ['GitHub', 'Portfolio']}
        ]
    },
    'devops_engineer': {
        'title': 'DevOps Engineer',
        'description': 'DevOps and cloud infrastructure path',
        'skills': [
            {'name': 'Linux & Command Line', 'level': 'Beginner', 'duration': '3 weeks', 'resources': ['Linux Journey', 'OverTheWire']},
            {'name': 'Networking Basics', 'level': 'Beginner', 'duration': '2 weeks', 'resources': ['Cisco Networking Basics', 'Computer Networking Course']},
            {'name': 'Git & Version Control', 'level': 'Beginner', 'duration': '1 week', 'resources': ['Git Documentation', 'Atlassian Git Tutorial']},
            {'name': 'Docker & Containers', 'level': 'Intermediate', 'duration': '4 weeks', 'resources': ['Docker Docs', 'Play with Docker']},
            {'name': 'CI/CD Pipelines', 'level': 'Intermediate', 'duration': '3 weeks', 'resources': ['Jenkins', 'GitHub Actions', 'GitLab CI']},
            {'name': 'Cloud Platforms (AWS/Azure/GCP)', 'level': 'Advanced', 'duration': '8 weeks', 'resources': ['AWS Training', 'Azure Learn', 'GCP Training']},
            {'name': 'Kubernetes', 'level': 'Advanced', 'duration': '6 weeks', 'resources': ['Kubernetes Docs', 'KodeKloud']},
            {'name': 'Infrastructure as Code', 'level': 'Advanced', 'duration': '4 weeks', 'resources': ['Terraform', 'Ansible']}
        ]
    },
    'ui_ux_designer': {
        'title': 'UI/UX Designer',
        'description': 'User interface and experience design path',
        'skills': [
            {'name': 'Design Fundamentals', 'level': 'Beginner', 'duration': '3 weeks', 'resources': ['Design Principles', 'Laws of UX']},
            {'name': 'Figma/Adobe XD', 'level': 'Beginner', 'duration': '4 weeks', 'resources': ['Figma Tutorial', 'Adobe XD Learn']},
            {'name': 'User Research', 'level': 'Intermediate', 'duration': '3 weeks', 'resources': ['Nielsen Norman Group', 'UX Research Methods']},
            {'name': 'Wireframing & Prototyping', 'level': 'Intermediate', 'duration': '4 weeks', 'resources': ['Balsamiq', 'InVision']},
            {'name': 'Visual Design', 'level': 'Intermediate', 'duration': '5 weeks', 'resources': ['Refactoring UI', 'Design Systems']},
            {'name': 'Interaction Design', 'level': 'Advanced', 'duration': '4 weeks', 'resources': ['Interaction Design Foundation', 'Microinteractions']},
            {'name': 'Usability Testing', 'level': 'Intermediate', 'duration': '2 weeks', 'resources': ['UserTesting.com', 'Hotjar']},
            {'name': 'Build Portfolio', 'level': 'Advanced', 'duration': 'Ongoing', 'resources': ['Behance', 'Dribbble']}
        ]
    }
}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, name):
        self.id = id
        self.email = email
        self.name = name

# Helper functions
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def send_welcome_email(user_email, user_name):
    """
    Send welcome email to new user
    Configure your email settings here
    """
    try:
        sender_email = "careerbuilder629@gmail.com"  # Change this
        sender_password = "cmfc qcwj lyrl bpio"  # Use App Password for Gmail
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = user_email
        msg['Subject'] = 'Welcome to Career Path Builder!'
        
        body = f"""
Hi {user_name},

Welcome to Career Path Builder! 🎉

We're excited to have you on board. You can now:
✓ Explore different career paths
✓ Identify your skill gaps
✓ Get personalized learning roadmaps
✓ Track your progress

Start your journey by selecting a career path from your dashboard.

Best regards,
Career Path Builder Team
"""
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    if user_id in users:
        user_data = users[user_id]
        return User(user_id, user_data['email'], user_data['name'])
    return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# ----------- REGISTER ROUTE (Corrected) ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password').strip()

        users = load_users()
        if not isinstance(users, dict):
            users = {}

        # Check if email already exists
        existing_user = None
        for u in users.values():
            if u.get('email', '').lower() == email:
                existing_user = u
                break

        if existing_user:
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))

        # Create new user
        user_id = str(len(users) + 1)
        users[user_id] = {
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'created_at': datetime.now().isoformat()
        }
        save_users(users)

        # Send welcome email
        email_sent = send_welcome_email(email, name)
        if email_sent:
            flash('Registration successful! Welcome email sent.', 'success')
        else:
            flash('Registration successful! ', 'success')

        return redirect(url_for('login'))

    return render_template('register.html')

# ----------- LOGIN ROUTE ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password').strip()
        users = load_users()

        user_data = None
        user_id = None
        for uid, udata in users.items():
            if udata.get('email', '').lower() == email:
                user_data = udata
                user_id = uid
                break

        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_id, user_data['email'], user_data['name'])
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    progress = load_progress()
    user_progress = progress.get(current_user.id, {})
    return render_template('dashboard.html', careers=CAREER_ROADMAPS, user_progress=user_progress)

@app.route('/career/<career_id>')
@login_required
def career_detail(career_id):
    if career_id not in CAREER_ROADMAPS:
        flash('Career path not found!', 'error')
        return redirect(url_for('dashboard'))

    career = CAREER_ROADMAPS[career_id]
    progress = load_progress()
    user_progress = progress.get(current_user.id, {}).get(career_id, {})

    return render_template('career_detail.html', career=career, career_id=career_id, user_progress=user_progress)

@app.route('/update_progress', methods=['POST'])
@login_required
def update_progress():
    career_id = request.form.get('career_id')
    skill_name = request.form.get('skill_name')
    completed = request.form.get('completed') == 'true'

    progress = load_progress()
    if current_user.id not in progress:
        progress[current_user.id] = {}
    if career_id not in progress[current_user.id]:
        progress[current_user.id][career_id] = {}

    progress[current_user.id][career_id][skill_name] = completed
    save_progress(progress)
    return {'success': True}

@app.route('/profile')
@login_required
def profile():
    users = load_users()
    user_data = users.get(current_user.id, {})

    progress = load_progress()
    user_progress = progress.get(current_user.id, {})

    total_skills = 0
    completed_skills = 0
    for career_id, skills in user_progress.items():
        total_skills += len(CAREER_ROADMAPS[career_id]['skills'])
        completed_skills += sum(1 for completed in skills.values() if completed)

    return render_template('profile.html', 
                           user_data=user_data, 
                           total_skills=total_skills,
                           completed_skills=completed_skills)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
