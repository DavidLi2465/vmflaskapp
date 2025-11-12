from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.security import generate_password_hash

app = Flask(__name__, instance_relative_config=True)
app.config['DATABASE'] = os.path.join(app.instance_path, 'users.db')
# Ensure the instance folder exists (kept out of source control)
os.makedirs(app.instance_path, exist_ok=True)


def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )'''
    )
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm', '').strip()

        if not username or not email or not password:
            error = 'Please fill out all fields.'
        elif password != confirm:
            error = 'Passwords do not match.'
        else:
            conn = get_db()
            cur = conn.cursor()
            try:
                hashed = generate_password_hash(password)
                cur.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                            (username, email, hashed))
                conn.commit()
                conn.close()
                return redirect(url_for('signup_success', username=username))
            except sqlite3.IntegrityError as e:
                conn.close()
                if 'username' in str(e).lower():
                    error = 'Username already taken.'
                elif 'email' in str(e).lower():
                    error = 'Email already registered.'
                else:
                    error = 'Database error.'

    return render_template('signup.html', error=error)


@app.route('/signup/success')
def signup_success():
    username = request.args.get('username')
    return render_template('success.html', username=username)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
