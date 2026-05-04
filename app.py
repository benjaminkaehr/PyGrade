from flask import Flask, render_template, request, jsonify, session
from flask_bcrypt import Bcrypt
import sqlite3
import os

app = Flask(__name__)
# In a real app, keep this secret and don't put it in the code!
app.secret_key = 'pygrade_super_secret_dev_key' 
bcrypt = Bcrypt(app)

# Serve the Frontend
@app.route('/')
def home():
    # This tells Flask to send your index.html file to the browser
    return render_template('index.html')

# Setup the database
def init_db():
    conn = sqlite3.connect('pygrade.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    # Later, we will add a 'grades' table here
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    # Run the server in debug mode so it updates when you save files
    app.run(debug=True, port=5000)