from candidate_portal.database import get_connection, create_tables
from flask import Flask, render_template, request, redirect, session, send_from_directory, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import get_connection, create_tables
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this to a random string

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required_candidate():
    """Check if candidate is logged in, redirect if not"""
    if 'candidate_id' not in session:
        flash('Please login to access the dashboard', 'error')
        return redirect('/candidate/login')
    return None

def login_required_recruiter():
    """Check if recruiter is logged in, redirect if not"""
    if 'recruiter_id' not in session:
        flash('Please login to access search', 'error')
        return redirect('/recruiter/login')
    return None

# ─── HOME ───────────────────────────────────────────

@app.route('/')
def index():
    """Home page with links to candidate and recruiter sections"""
    return render_template('index.html')

# ─── CANDIDATE ROUTES ────────────────────────────────

@app.route('/candidate/register', methods=['GET', 'POST'])
def candidate_register():
    """Handle candidate registration"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        skills = request.form.get('skills', '').strip()
        experience_years = request.form.get('experience_years', '')
        location = request.form.get('location', '').strip()
        
        # Validation
        errors = []
        if not name:
            errors.append('Name is required')
        if not email:
            errors.append('Email is required')
        if not password:
            errors.append('Password is required')
        if not skills:
            errors.append('Skills are required')
        if not experience_years:
            errors.append('Experience years are required')
        elif not experience_years.isdigit():
            errors.append('Experience years must be a number')
        if not location:
            errors.append('Location is required')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('candidate_register.html')
        
        try:
            # Hash password
            hashed_password = generate_password_hash(password)
            
            # Insert into database
            conn = get_connection()
            conn.execute('''
                INSERT INTO candidates (name, email, password, skills, experience_years, location)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, email, hashed_password, skills, int(experience_years), location))
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect('/candidate/login')
            
        except sqlite3.IntegrityError:
            flash('Email already exists. Please use a different email.', 'error')
            return render_template('candidate_register.html')
    
    # GET request - show registration form
    return render_template('candidate_register.html')

@app.route('/candidate/login', methods=['GET', 'POST'])
def candidate_login():
    """Handle candidate login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('candidate_login.html')
        
        # Get candidate from database
        conn = get_connection()
        candidate = conn.execute(
            'SELECT * FROM candidates WHERE email = ?',
            (email,)
        ).fetchone()
        conn.close()
        
        if candidate and check_password_hash(candidate['password'], password):
            # Login successful
            session['candidate_id'] = candidate['id']
            session['candidate_name'] = candidate['name']
            flash('Login successful!', 'success')
            return redirect('/candidate/dashboard')
        else:
            # Login failed
            flash('Invalid email or password', 'error')
            return render_template('candidate_login.html')
    
    # GET request - show login form
    return render_template('candidate_login.html')

@app.route('/candidate/dashboard', methods=['GET', 'POST'])
def candidate_dashboard():
    """Candidate dashboard - view and update profile, upload resume"""
    # Check if candidate is logged in
    redirect_response = login_required_candidate()
    if redirect_response:
        return redirect_response
    
    candidate_id = session['candidate_id']
    conn = get_connection()
    
    if request.method == 'POST':
        # Handle profile update
        if 'update_profile' in request.form:
            name = request.form.get('name', '').strip()
            skills = request.form.get('skills', '').strip()
            experience_years = request.form.get('experience_years', '')
            location = request.form.get('location', '').strip()
            
            # Validation
            errors = []
            if not name:
                errors.append('Name is required')
            if not skills:
                errors.append('Skills are required')
            if not experience_years:
                errors.append('Experience years are required')
            elif not experience_years.isdigit():
                errors.append('Experience years must be a number')
            if not location:
                errors.append('Location is required')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
            else:
                # Update profile
                conn.execute('''
                    UPDATE candidates 
                    SET name = ?, skills = ?, experience_years = ?, location = ?
                    WHERE id = ?
                ''', (name, skills, int(experience_years), location, candidate_id))
                conn.commit()
                session['candidate_name'] = name
                flash('Profile updated successfully!', 'success')
        
        # Handle resume upload
        elif 'upload_resume' in request.form:
            if 'resume' not in request.files:
                flash('No file selected', 'error')
            else:
                file = request.files['resume']
                if file.filename == '':
                    flash('No file selected', 'error')
                elif file and allowed_file(file.filename):
                    # Secure the filename and save
                    filename = secure_filename(f"{candidate_id}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    
                    # Update database with filename
                    conn.execute(
                        'UPDATE candidates SET resume_filename = ? WHERE id = ?',
                        (filename, candidate_id)
                    )
                    conn.commit()
                    flash('Resume uploaded successfully!', 'success')
                else:
                    flash('Only PDF files are allowed', 'error')
    
    # Get candidate data for display
    candidate = conn.execute(
        'SELECT * FROM candidates WHERE id = ?',
        (candidate_id,)
    ).fetchone()
    conn.close()
    
    return render_template('candidate_dashboard.html', candidate=candidate)

@app.route('/candidate/logout')
def candidate_logout():
    """Logout candidate"""
    session.pop('candidate_id', None)
    session.pop('candidate_name', None)
    flash('You have been logged out', 'info')
    return redirect('/candidate/login')

# ─── RECRUITER ROUTES ────────────────────────────────

@app.route('/recruiter/login', methods=['GET', 'POST'])
def recruiter_login():
    """Handle recruiter login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('recruiter_login.html')
        
        # Get recruiter from database
        conn = get_connection()
        recruiter = conn.execute(
            'SELECT * FROM recruiters WHERE email = ?',
            (email,)
        ).fetchone()
        conn.close()
        
        if recruiter and check_password_hash(recruiter['password'], password):
            # Login successful
            session['recruiter_id'] = recruiter['id']
            session['recruiter_email'] = recruiter['email']
            flash('Login successful!', 'success')
            return redirect('/recruiter/search')
        else:
            # Login failed
            flash('Invalid email or password', 'error')
            return render_template('recruiter_login.html')
    
    # GET request - show login form
    return render_template('recruiter_login.html')

@app.route('/recruiter/search', methods=['GET', 'POST'])
def recruiter_search():
    """Recruiter search page with filters"""
    # Check if recruiter is logged in
    redirect_response = login_required_recruiter()
    if redirect_response:
        return redirect_response
    
    results = []
    search_performed = False
    
    if request.method == 'POST':
        # Get filter values
        skill = request.form.get('skill', '').strip()
        min_exp = request.form.get('min_exp', '').strip()
        location = request.form.get('location', '').strip()
        email = request.form.get('email', '').strip()
        
        # Build dynamic query
        query = 'SELECT * FROM candidates WHERE 1=1'
        params = []
        
        if skill:
            query += ' AND skills LIKE ?'
            params.append(f'%{skill}%')
        
        if min_exp:
            if min_exp.isdigit():
                query += ' AND experience_years >= ?'
                params.append(int(min_exp))
            else:
                flash('Minimum experience must be a number', 'error')
        
        if location:
            query += ' AND location LIKE ?'
            params.append(f'%{location}%')
        
        if email:
            query += ' AND email LIKE ?'
            params.append(f'%{email}%')
        
        # Execute search
        conn = get_connection()
        results = conn.execute(query, params).fetchall()
        conn.close()
        
        search_performed = True
        
        if not results:
            flash('No candidates found matching your criteria', 'info')
    
    return render_template('recruiter_search.html', results=results, search_performed=search_performed)

@app.route('/recruiter/logout')
def recruiter_logout():
    """Logout recruiter"""
    session.pop('recruiter_id', None)
    session.pop('recruiter_email', None)
    flash('You have been logged out', 'info')
    return redirect('/recruiter/login')

# ─── FILE SERVING ────────────────────────────────────

@app.route('/uploads/<filename>')
def serve_resume(filename):
    """Serve uploaded resume files (protected - recruiter only)"""
    # Check if recruiter is logged in
    if 'recruiter_id' not in session:
        flash('Please login as recruiter to download resumes', 'error')
        return redirect('/recruiter/login')
    
    # Security: ensure filename doesn't contain path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        flash('Invalid filename', 'error')
        return redirect('/recruiter/search')
    
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        flash('Resume file not found', 'error')
        return redirect('/recruiter/search')

# ─── ERROR HANDLERS ──────────────────────────────────

@app.errorhandler(413)
def too_large(e):
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect('/candidate/dashboard')

# ─── RUN ─────────────────────────────────────────────

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)