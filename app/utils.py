import os
from functools import wraps
from flask import current_app, flash, redirect, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename

def save_picture(form_picture):
    if form_picture:
        filename = secure_filename(form_picture.filename)
        picture_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], filename)
        # Ensure directory exists
        os.makedirs(os.path.dirname(picture_path), exist_ok=True)
        form_picture.save(picture_path)
        return filename
    return None

def superuser_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_superadmin:
            flash("У вас недостатньо прав.", "danger")
            return redirect(url_for('admin.admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function
