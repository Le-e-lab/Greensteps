from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Remove these duplicate lines
# app.config.from_object('config.Config')
# app.secret_key = app.config['SECRET_KEY']

# Database initialization
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        points INTEGER DEFAULT 0,
        badges TEXT DEFAULT ''
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        action_type TEXT NOT NULL,
        points_earned INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Helper functions
# Add near helper functions
from contextlib import contextmanager

@contextmanager
def db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Routes
# Add to your index route
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    with db_connection() as conn:
        cursor = conn.cursor()
        
        # Get user data
        cursor.execute('SELECT username, points, badges FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        
        if not user:
            session.pop('user_id', None)
            return redirect(url_for('login'))
        
        # Get leaderboard
        cursor.execute('SELECT username, points FROM users ORDER BY points DESC LIMIT 5')
        leaderboard = cursor.fetchall()
        
        # Get recent actions
        cursor.execute('''
            SELECT action_type, points_earned, timestamp 
            FROM actions 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 5
        ''', (session['user_id'],))
        actions = cursor.fetchall()
        
        # Calculate statistics
        cursor.execute('SELECT COUNT(*) FROM actions WHERE user_id = ? AND action_type = "bike"', (session['user_id'],))
        bike_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM actions WHERE user_id = ? AND action_type = "plant_tree"', (session['user_id'],))
        tree_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM actions WHERE user_id = ? AND action_type = "recycle"', (session['user_id'],))
        recycle_count = cursor.fetchone()[0]
        recycle_kg = recycle_count * 1.5  # Assuming 1.5kg per recycling action
        
        # Calculate CO₂ savings
        cursor.execute('SELECT SUM(points_earned) FROM actions WHERE user_id = ?', (session['user_id'],))
        total_points = cursor.fetchone()[0] or 0
        co2_saved = round(total_points * 0.1, 2)
        
        # In the index route, modify the return statement:
        return render_template(
            'index.html',
            user=dict(user),
            leaderboard=leaderboard,
            actions=actions,
            co2_saved=co2_saved,
            bike_count=bike_count,
            tree_count=tree_count,
            recycle_kg=recycle_kg,
            # Add this new context variable
            new_achievements=session.pop('new_achievements', [])
        )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error='Username and password are required')
        
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, password FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                return redirect(url_for('index'))
            
        return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        with db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                user_id = cursor.lastrowid
                session['user_id'] = user_id
                return redirect(url_for('index'))
            except sqlite3.IntegrityError:
                return render_template('register.html', error='Username already exists')
    
    return render_template('register.html')

# Add configuration to a separate config file
app.config.from_object('config.Config')
app.secret_key = app.config['SECRET_KEY']

# Add error handling
# Replace existing error handlers with these
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_code=404,
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html',
                         error_code=500,
                         error_message="Internal server error"), 500

# Add input validation to log-action
@app.route('/log-action', methods=['POST'])
def log_action():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    action_type = request.form.get('action_type')
    points_map = {
        'bike': 50,
        'recycle': 30,
        'plant_tree': 100,
        'meatless_meal': 20
    }
    
    if action_type not in points_map:
        return redirect(url_for('index'))
    
    points = points_map[action_type]
    
    with db_connection() as conn:
        cursor = conn.cursor()
        # Log action
        cursor.execute(
            'INSERT INTO actions (user_id, action_type, points_earned) VALUES (?, ?, ?)',
            (session['user_id'], action_type, points)
        )
        
        # Update user points
        cursor.execute(
            'UPDATE users SET points = points + ? WHERE id = ?',
            (points, session['user_id'])
        )
        
        conn.commit()
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# At the bottom of the file, modify this section
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


# In the log_action route after updating points:
new_achievements = []
if action_type == 'plant_tree' and (tree_count + 1) == 5:
    new_achievements.append('tree_pioneer')
elif action_type == 'bike' and (bike_count + 1) == 10:
    new_achievements.append('cycling_hero')
elif action_type == 'recycle' and ((recycle_count + 1) * 1.5) >= 30:
    new_achievements.append('recycling_pro')

if new_achievements:
    session['new_achievements'] = new_achievements