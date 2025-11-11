import os
import secrets
import pdfplumber
from PyPDF2 import PdfReader
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, date, timedelta
import json

from syllabus_processor import extract_topics
from scheduler import generate_schedule
from video_recommender import recommend_videos
from models import db, User, Topic, StudySession, Calendar, CalendarEvent, ProgressAnalytics, StudyNote, Flashcard, StudyGoal, Deadline, StudyStreak
from topic_categorizer import AdvancedTopicCategorizer
from calendar_integration import CalendarIntegration
from progress_tracker import ProgressTracker
from pomodoro_timer import PomodoroTimer
from notes_manager import NotesManager
from flashcard_generator import FlashcardGenerator
from goal_manager import GoalManager
from deadline_manager import DeadlineManager
from streak_tracker import StreakTracker
from export_manager import ExportManager
from ai_recommender import AIRecommender

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or secrets.token_hex(16)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize feature modules
topic_categorizer = AdvancedTopicCategorizer()
calendar_integration = CalendarIntegration()
progress_tracker = ProgressTracker()
pomodoro_timer = PomodoroTimer()
notes_manager = NotesManager()
flashcard_generator = FlashcardGenerator()
goal_manager = GoalManager()
deadline_manager = DeadlineManager()
streak_tracker = StreakTracker()
export_manager = ExportManager()
ai_recommender = AIRecommender()

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def pull_text_from_pdf(filepath):
    """Extract text from PDF using pdfplumber, fallback to PyPDF2."""
    text_chunks = []
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                txt = page.extract_text()
                if txt:
                    text_chunks.append(txt)
    except Exception as e:
        app.logger.warning(f"pdfplumber error: {e}")

    full_text = "\n".join(text_chunks).strip()
    if full_text:
        return full_text

    try:
        reader = PdfReader(filepath)
        fallback = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                fallback.append(t)
        return "\n".join(fallback).strip()
    except Exception as err:
        flash(f"PDF parse error: {err}", 'danger')
        return None


def pull_text_from_txt(filepath):
    """Read text safely with multiple encodings."""
    for enc in ('utf-8', 'latin-1', 'utf-16'):
        try:
            with open(filepath, 'r', encoding=enc) as f:
                data = f.read()
                if data:
                    return data.strip()
        except Exception as e:
            app.logger.debug(f"[TXT-{enc}] read error: {e}")
            continue
    flash("Unable to read text file (tried UTF-8, Latin-1, UTF-16).", 'danger')
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not allowed_file(file.filename):
            flash("Only PDF or TXT files are allowed.", 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        # Extract text
        text = pull_text_from_pdf(path) if filename.lower().endswith('.pdf') else pull_text_from_txt(path)
        os.remove(path)

        if not text:
            flash("No text could be extracted from the file.", 'danger')
            return redirect(request.url)

        topics = extract_topics(text)
        if not topics:
            flash("No valid topics found in the syllabus file.", 'warning')
            return redirect(request.url)

        session['topics'] = topics
        return redirect(url_for('dashboard'))

    return render_template('upload.html')


@app.route('/dashboard')
def dashboard():
    topics = session.get('topics', [])
    if not topics:
        flash("Please upload a syllabus first.", 'info')
        return redirect(url_for('upload'))

    video_links = recommend_videos(topics)
    return render_template('dashboard.html', topics=topics, video_links=video_links)


@app.route('/analyze_and_plan', methods=['POST'])
def analyze_and_plan():
    topics = session.get('topics', [])
    if not topics:
        flash("No topics found. Please upload a syllabus first.", 'warning')
        return redirect(url_for('upload'))
    
    # Enhanced topic processing with categorization
    enhanced_topics = []
    for topic_name in topics:
        categorization = topic_categorizer.categorize_topic(topic_name)
        enhanced_topic = {
            'name': topic_name,
            'category': categorization['category'],
            'subcategory': categorization['subcategory'],
            'difficulty': categorization['difficulty'],
            'estimated_hours': categorization['estimated_hours'],
            'priority': categorization['priority'],
            'confidence': categorization['confidence']
        }
        enhanced_topics.append(enhanced_topic)
    
    # Generate smart calendar-integrated schedule
    start_date = date.today()
    smart_schedule = calendar_integration.generate_smart_schedule(enhanced_topics, start_date)
    
    # Store enhanced data in session
    session['enhanced_topics'] = enhanced_topics
    session['smart_schedule'] = smart_schedule
    
    return render_template('result.html', 
                         schedule=smart_schedule, 
                         enhanced_topics=enhanced_topics,
                         video_links=recommend_videos(topics))

# New routes for enhanced features

@app.route('/calendar')
def calendar_view():
    """Display calendar view of study schedule"""
    smart_schedule = session.get('smart_schedule', {})
    if not smart_schedule:
        flash("Please generate a study plan first.", 'info')
        return redirect(url_for('upload'))
    
    calendar_view = calendar_integration.get_calendar_view(smart_schedule, 'week')
    return render_template('calendar.html', calendar_data=calendar_view)

@app.route('/export_calendar/<format_type>')
def export_calendar(format_type):
    """Export calendar to various formats"""
    smart_schedule = session.get('smart_schedule', {})
    if not smart_schedule:
        return jsonify({'error': 'No schedule found'}), 400
    
    exported_data = calendar_integration.export_to_calendar_format(smart_schedule, format_type)
    
    if format_type == 'ics':
        from flask import Response
        return Response(exported_data, mimetype='text/calendar', 
                       headers={'Content-Disposition': 'attachment; filename=study_schedule.ics'})
    else:
        return jsonify(json.loads(exported_data))

@app.route('/progress')
def progress_dashboard():
    """Display progress tracking dashboard"""
    # Mock data for demonstration - in production, this would fetch from database
    mock_progress = {
        'daily_progress': [
            {
                'date': (date.today() - timedelta(days=i)).isoformat(),
                'total_study_time': 120 + (i * 30),
                'topics_completed': 2 + i,
                'productivity_score': 75 + (i * 5)
            }
            for i in range(7)
        ],
        'weekly_summary': {
            'total_study_hours': 15.5,
            'average_productivity_score': 78.5,
            'study_streak_days': 5,
            'progress_trend': 'improving'
        }
    }
    
    return render_template('progress.html', progress_data=mock_progress)

@app.route('/track_session', methods=['POST'])
def track_study_session():
    """Track a study session"""
    data = request.get_json()
    
    session_data = progress_tracker.track_study_session(
        user_id=1,  # Mock user ID
        topic_id=data.get('topic_id'),
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
        progress_percentage=data.get('progress_percentage', 0),
        notes=data.get('notes', '')
    )
    
    return jsonify(session_data)

@app.route('/analytics')
def analytics_dashboard():
    """Display detailed analytics"""
    # Mock analytics data
    analytics_data = {
        'study_patterns': {
            'most_productive_time': 'Morning (8-12 AM)',
            'average_session_length': 45,
            'preferred_study_days': ['Monday', 'Wednesday', 'Friday']
        },
        'topic_performance': {
            'strongest_category': 'Programming',
            'challenging_category': 'Mathematics',
            'completion_rate': 78.5
        },
        'recommendations': [
            'Focus more on morning study sessions',
            'Break down complex mathematics topics',
            'Increase study time on weekends'
        ]
    }
    
    return render_template('analytics.html', analytics_data=analytics_data)

@app.route('/topics')
def topics_management():
    """Display categorized topics with management options"""
    enhanced_topics = session.get('enhanced_topics', [])
    if not enhanced_topics:
        flash("Please upload and process a syllabus first.", 'info')
        return redirect(url_for('upload'))
    
    # Group topics by category
    topics_by_category = {}
    for topic in enhanced_topics:
        category = topic['category']
        if category not in topics_by_category:
            topics_by_category[category] = []
        topics_by_category[category].append(topic)
    
    return render_template('topics.html', 
                         topics_by_category=topics_by_category,
                         total_topics=len(enhanced_topics))

@app.route('/api/topic_recommendations/<int:topic_id>')
def get_topic_recommendations(topic_id):
    """Get personalized recommendations for a topic"""
    enhanced_topics = session.get('enhanced_topics', [])
    topic = next((t for t in enhanced_topics if t.get('id') == topic_id), None)
    
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404
    
    recommendations = topic_categorizer.get_study_recommendations(topic)
    return jsonify({'recommendations': recommendations})

@app.route('/api/progress_export/<format_type>')
def export_progress(format_type):
    """Export progress data"""
    # Mock progress data
    progress_data = {
        'daily_progress': [
            {
                'date': (date.today() - timedelta(days=i)).isoformat(),
                'total_study_time': 120 + (i * 30),
                'topics_completed': 2 + i,
                'productivity_score': 75 + (i * 5)
            }
            for i in range(30)
        ]
    }
    
    exported_data = progress_tracker.export_progress_report(progress_data, format_type)
    
    if format_type == 'csv':
        from flask import Response
        return Response(exported_data, mimetype='text/csv',
                       headers={'Content-Disposition': 'attachment; filename=progress_report.csv'})
    else:
        return jsonify(json.loads(exported_data))

# New routes for additional features

@app.route('/pomodoro')
def pomodoro_timer_page():
    """Pomodoro timer page"""
    return render_template('pomodoro.html')

@app.route('/api/pomodoro/start', methods=['POST'])
def start_pomodoro():
    """Start a Pomodoro session"""
    data = request.get_json()
    work_duration = data.get('work_duration', 25)
    break_duration = data.get('break_duration', 5)
    
    session_data = pomodoro_timer.start_session(work_duration, break_duration)
    return jsonify(session_data)

@app.route('/api/pomodoro/break', methods=['POST'])
def start_break():
    """Start a break session"""
    data = request.get_json()
    is_long_break = data.get('is_long_break', False)
    
    break_data = pomodoro_timer.start_break(is_long_break=is_long_break)
    return jsonify(break_data)

@app.route('/notes')
def notes_page():
    """Study notes management page"""
    # Mock notes data - in production, fetch from database
    mock_notes = []
    enhanced_topics = session.get('enhanced_topics', [])
    return render_template('notes.html', notes=mock_notes, topics=enhanced_topics)

@app.route('/api/notes/create', methods=['POST'])
def create_note():
    """Create a new study note"""
    data = request.get_json()
    note = notes_manager.create_note(
        topic_id=data.get('topic_id'),
        title=data.get('title'),
        content=data.get('content')
    )
    return jsonify(note)

@app.route('/api/notes/search', methods=['POST'])
def search_notes():
    """Search notes"""
    data = request.get_json()
    query = data.get('query', '')
    notes = []  # Fetch from database
    results = notes_manager.search_notes(notes, query)
    return jsonify({'results': results})

@app.route('/flashcards')
def flashcards_page():
    """Flashcards page"""
    enhanced_topics = session.get('enhanced_topics', [])
    mock_flashcards = []
    return render_template('flashcards.html', flashcards=mock_flashcards, topics=enhanced_topics)

@app.route('/api/flashcards/generate', methods=['POST'])
def generate_flashcards():
    """Generate flashcards from topic"""
    data = request.get_json()
    topic_name = data.get('topic_name', '')
    topic_content = data.get('topic_content', '')
    count = data.get('count', 5)
    
    flashcards = flashcard_generator.generate_flashcards_from_topic(topic_name, topic_content, count)
    return jsonify({'flashcards': flashcards})

@app.route('/api/flashcards/study', methods=['POST'])
def study_flashcard():
    """Update flashcard mastery after studying"""
    data = request.get_json()
    flashcard = data.get('flashcard', {})
    was_correct = data.get('was_correct', False)
    
    new_mastery = flashcard_generator.update_mastery_level(flashcard, was_correct)
    flashcard['mastery_level'] = new_mastery
    flashcard['times_studied'] = flashcard.get('times_studied', 0) + 1
    flashcard['last_studied'] = datetime.now().isoformat()
    
    return jsonify(flashcard)

@app.route('/goals')
def goals_page():
    """Study goals page"""
    mock_goals = []
    return render_template('goals.html', goals=mock_goals)

@app.route('/api/goals/create', methods=['POST'])
def create_goal():
    """Create a new study goal"""
    data = request.get_json()
    target_date = datetime.fromisoformat(data['target_date']).date() if isinstance(data['target_date'], str) else data['target_date']
    
    goal = goal_manager.create_goal(
        title=data.get('title'),
        description=data.get('description', ''),
        target_date=target_date,
        target_hours=data.get('target_hours', 0.0)
    )
    return jsonify(goal)

@app.route('/api/goals/update', methods=['POST'])
def update_goal():
    """Update goal progress"""
    data = request.get_json()
    goal = data.get('goal', {})
    hours_studied = data.get('hours_studied', 0.0)
    
    updated_goal = goal_manager.update_goal_progress(goal, hours_studied)
    return jsonify(updated_goal)

@app.route('/deadlines')
def deadlines_page():
    """Deadlines management page"""
    mock_deadlines = []
    upcoming = deadline_manager.get_upcoming_deadlines(mock_deadlines, days=30)
    overdue = deadline_manager.get_overdue_deadlines(mock_deadlines)
    return render_template('deadlines.html', deadlines=mock_deadlines, upcoming=upcoming, overdue=overdue)

@app.route('/api/deadlines/create', methods=['POST'])
def create_deadline():
    """Create a new deadline"""
    data = request.get_json()
    deadline_date = datetime.fromisoformat(data['deadline_date']) if isinstance(data['deadline_date'], str) else data['deadline_date']
    
    deadline = deadline_manager.create_deadline(
        title=data.get('title'),
        description=data.get('description', ''),
        deadline_date=deadline_date,
        priority=data.get('priority', 'Medium')
    )
    return jsonify(deadline)

@app.route('/streak')
def streak_page():
    """Study streak page"""
    mock_streak = {
        'current_streak': 5,
        'longest_streak': 12,
        'last_study_date': date.today().isoformat(),
        'total_study_days': 45
    }
    streak_info = streak_tracker.get_streak_info(mock_streak)
    milestones = streak_tracker.get_milestones(mock_streak)
    return render_template('streak.html', streak_info=streak_info, milestones=milestones)

@app.route('/api/streak/update', methods=['POST'])
def update_streak():
    """Update study streak"""
    data = request.get_json()
    streak_data = data.get('streak_data', {})
    study_date = datetime.fromisoformat(data['study_date']).date() if isinstance(data['study_date'], str) else data['study_date']
    
    updated_streak = streak_tracker.update_streak(streak_data, study_date)
    return jsonify(updated_streak)

@app.route('/export')
def export_page():
    """Export study data page"""
    smart_schedule = session.get('smart_schedule', {})
    progress_data = []
    goals = []
    return render_template('export.html', schedule=smart_schedule, progress=progress_data, goals=goals)

@app.route('/api/export/schedule/<format_type>')
def export_schedule(format_type):
    """Export schedule in various formats"""
    smart_schedule = session.get('smart_schedule', {})
    
    if format_type == 'json':
        exported = export_manager.export_schedule_to_json(smart_schedule)
        from flask import Response
        return Response(exported, mimetype='application/json',
                       headers={'Content-Disposition': 'attachment; filename=schedule.json'})
    elif format_type == 'csv':
        exported = export_manager.export_schedule_to_csv(smart_schedule)
        from flask import Response
        return Response(exported, mimetype='text/csv',
                       headers={'Content-Disposition': 'attachment; filename=schedule.csv'})
    else:
        return jsonify({'error': 'Invalid format'}), 400

@app.route('/api/export/report')
def export_report():
    """Export comprehensive study report"""
    smart_schedule = session.get('smart_schedule', {})
    progress_data = []
    goals = []
    
    report = export_manager.create_study_report(smart_schedule, progress_data, goals)
    from flask import Response
    return Response(report, mimetype='text/plain',
                   headers={'Content-Disposition': 'attachment; filename=study_report.txt'})

@app.route('/recommendations')
def recommendations_page():
    """AI recommendations page"""
    progress_data = []
    enhanced_topics = session.get('enhanced_topics', [])
    study_sessions = []
    
    recommendations = ai_recommender.get_study_recommendations(progress_data, enhanced_topics, study_sessions)
    topic_recommendations = ai_recommender.recommend_topics_to_study(enhanced_topics, progress_data)
    optimal_time = ai_recommender.get_optimal_study_time(progress_data)
    
    return render_template('recommendations.html', 
                         recommendations=recommendations,
                         topic_recommendations=topic_recommendations,
                         optimal_time=optimal_time)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
