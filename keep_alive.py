from flask import Flask, send_from_directory, render_template, jsonify, url_for
from flask_cors import CORS
import os
from threading import Thread
from .shared import user_cache

app = Flask(__name__)
CORS(app)
USER_IMAGE_DIR = "user_images"

# ─── 静的ファイル配信用エンドポイント ───
@app.route('/user_images/<path:filename>')
def user_image(filename):
    return send_from_directory(USER_IMAGE_DIR, filename)

# ─── HTMLギャラリー ───
@app.route('/')
def index():
    folders = []
    for user_id in sorted(os.listdir(USER_IMAGE_DIR)):
        user_path = os.path.join(USER_IMAGE_DIR, user_id)
        if not os.path.isdir(user_path):
            continue

        pngs = [
            f"{user_id}/{f}"
            for f in os.listdir(user_path)
            if f.lower().endswith('.png')
        ]
        username = user_cache.get(user_id, f"Unknown ({user_id})")
        folders.append({"user": username, "images": pngs})

    return render_template('index.html', folders=folders)

# ─── JSON API ───
@app.route('/api/users')
def api_users():
    folders = []
    for user_id in sorted(os.listdir(USER_IMAGE_DIR)):
        user_path = os.path.join(USER_IMAGE_DIR, user_id)
        if not os.path.isdir(user_path):
            continue

        pngs = [
            f"{user_id}/{fname}"
            for fname in os.listdir(user_path)
            if fname.lower().endswith('.png')
        ]
        username = user_cache.get(user_id, f"Unknown ({user_id})")
        image_urls = [
            url_for('user_image', filename=path, _external=True)
            for path in pngs
        ]
        folders.append({"user": username, "images": image_urls})

    return jsonify(folders)

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)

def keep_alive():
    server = Thread(target=run)
    server.daemon = True
    server.start()
