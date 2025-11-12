from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.security import check_password_hash
load_dotenv()
#111111
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
original_container = "original"
thumbnail_container = "thumbnail"

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        db.close()

        # check password hashed
        if user and check_password_hash(user['hashed_password'], password):
            session['user_id'] = user['userID']
            return redirect(url_for('upload_file'))
        else:
            return "Invalid username or password"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (username, hashed_password) VALUES (%s, %s)",
            (username, hashed_pw)
        )
        db.commit()
        db.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/upload', methods=['GET','POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename != '':
            blob_client = blob_service_client.get_blob_client(
                container=original_container,
                blob=file.filename
            )
            blob_client.upload_blob(file.read(), overwrite=True)

            original_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{original_container}/{file.filename}"

            cursor.execute(
                "INSERT INTO images (ownerUserID, originalURL) VALUES (%s, %s)",
                (session['user_id'], original_url)
            )
            db.commit()
            db.close()
            return redirect(url_for('upload_file'))

    
    cursor.execute("""
        SELECT originalURL, caption
        FROM images
        WHERE ownerUserID = %s
        ORDER BY imageID DESC
    """, (session['user_id'],))
    originals = cursor.fetchall()

    # 查询缩略图（只取有 thumbnailURL 的记录）
    cursor.execute("""
        SELECT thumbnailURL, caption
        FROM images
        WHERE ownerUserID = %s AND thumbnailURL IS NOT NULL
        ORDER BY imageID DESC
    """, (session['user_id'],))
    thumbnails = cursor.fetchall()

    db.close()
    return render_template('index.html', blobs=originals, thumbnails=thumbnails)
