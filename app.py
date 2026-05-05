from flask import Flask, render_template, request, jsonify, session
from flask_bcrypt import Bcrypt
import sqlite3
import json

app = Flask(__name__)
# Security key for session cookies
app.secret_key = 'pygrade_super_secret_dev_key' 
bcrypt = Bcrypt(app)

def get_db_connection():
    conn = sqlite3.connect('pygrade.db')
    conn.row_factory = sqlite3.Row # Allows us to access columns by name
    return conn

# --- DATABASE SETUP ---
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    # Create Data table to store grades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_data (
            user_id INTEGER PRIMARY KEY,
            data_json TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

# --- WEB ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

# --- API ROUTES FOR AUTHENTICATION ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    conn = get_db_connection()
    
    try:
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        return jsonify({"message": "Registration successful!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    user = conn.execute("SELECT id, username, password_hash FROM users WHERE username=?", (username,)).fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({"message": "Login successful!"}), 200
    
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200

# --- API ROUTES FOR GRADES ---
@app.route('/api/data', methods=['GET'])
def get_data():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db_connection()
    row = conn.execute("SELECT data_json FROM user_data WHERE user_id=?", (session['user_id'],)).fetchone()
    conn.close()
    
    if row and row['data_json']:
        return jsonify({"subjects": json.loads(row['data_json'])})
    return jsonify({"subjects": {}})

@app.route('/api/data', methods=['POST'])
def save_data():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data_json = json.dumps(request.json.get('subjects', {}))
    
    conn = get_db_connection()
    # Insert or Update the user's data
    conn.execute('''
        INSERT INTO user_data (user_id, data_json) 
        VALUES (?, ?) 
        ON CONFLICT(user_id) DO UPDATE SET data_json=excluded.data_json
    ''', (session['user_id'], data_json))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Data saved successfully!"}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)