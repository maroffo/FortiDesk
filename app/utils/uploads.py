# ABOUTME: File upload utilities for saving, deleting, and validating uploads
# ABOUTME: Uses UUID naming to prevent conflicts and directory traversal

import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file):
    """Save uploaded file with UUID name. Returns (saved_path, original_filename, file_size, mime_type)."""
    if not file or not file.filename:
        return None

    original_filename = secure_filename(file.filename)
    if not allowed_file(original_filename):
        return None

    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    save_path = os.path.join(upload_folder, unique_name)
    file.save(save_path)

    file_size = os.path.getsize(save_path)
    mime_type = file.content_type

    return save_path, original_filename, file_size, mime_type


def delete_upload(file_path):
    """Delete an uploaded file from disk."""
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
