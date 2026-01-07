from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
import os
from models import db
from models.User import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/update-avatar/<int:user_id>', methods=['POST'])
def update_avatar(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if 'avatar' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    allowed_ext = {'png', 'jpg', 'jpeg', 'gif'}
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed_ext:
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(f"user_{user.id}.{ext}")

    upload_folder = os.path.join(
        current_app.root_path,
        'static/uploads/avatars'
    )
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    user.avatar = f"/static/uploads/avatars/{filename}"
    db.session.commit()        # ✅ OK

    session['user_avatar'] = user.avatar

    return jsonify({
        "message": "Update avatar success",
        "avatar": user.avatar
    })
