from flask import Blueprint, render_template, request, redirect, session
# 23130071 thêm vào
import os
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from models.User import User
from app import db

@user_bp.route('/update-avatar/<int:user_id>', methods=['POST'])
def update_avatar(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if 'avatar' not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files['avatar']
    filename = secure_filename(file.filename)

    upload_folder = os.path.join(current_app.root_path, 'static/uploads/avatars')
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    user.avatar = f"/static/uploads/avatars/{filename}"
    db.session.commit()

    return jsonify({
        "message": "Update avatar success",
        "avatar": user.avatar
    })

