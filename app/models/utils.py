import os
import uuid
from flask import current_app, request
from werkzeug.utils import secure_filename
from app.models.db import query_db


def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS'])


def save_upload(file, folder_key):
    """Save an uploaded file and return the stored filename (or None)."""
    if not file or file.filename == '':
        return None
    if not allowed_file(file.filename):
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    folder = current_app.config[folder_key]
    file.save(os.path.join(folder, unique_name))
    return unique_name


def log_activity(user_id, action, description=''):
    """Persist an activity record for audit/suspicious-activity monitoring."""
    ip  = request.remote_addr
    ua  = request.headers.get('User-Agent', '')[:500]
    query_db(
        "INSERT INTO activity_log (user_id, action, description, ip_address, user_agent) "
        "VALUES (%s, %s, %s, %s, %s)",
        (user_id, action, description, ip, ua),
        commit=True
    )


def progress_percent(current, target):
    if not target or target == 0:
        return 0
    pct = (float(current) / float(target)) * 100
    return min(round(pct, 1), 100)
