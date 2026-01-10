from flask import Blueprint, render_template, request, redirect, flash, url_for
from models.User import User
from models import db
from datetime import datetime
from services.email_service import send_reset_password_email

password_bp = Blueprint("password", __name__)

# ======================
# FORM QUÊN MẬT KHẨU
# ======================
@password_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            send_reset_password_email(user)

        flash("Nếu email tồn tại, link đặt lại mật khẩu đã được gửi.", "info")
        return redirect('/login')

    return render_template('forgot_password.html')


# ======================
# RESET MẬT KHẨU
# ======================
@password_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_password_token=token).first()

    if not user or user.reset_password_expires < datetime.utcnow():
        flash("Link không hợp lệ hoặc đã hết hạn", "danger")
        return redirect('/login')

    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if password != confirm:
            flash("Mật khẩu không khớp", "danger")
            return render_template('reset_password.html')

        # ⚠️ demo chưa hash (nên hash ở production)
        user.password_hash = password
        user.reset_password_token = None
        user.reset_password_expires = None
        db.session.commit()

        flash("Đặt lại mật khẩu thành công. Vui lòng đăng nhập.", "success")
        return redirect('/login')

    return render_template('reset_password.html')
