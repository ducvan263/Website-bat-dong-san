from flask import Blueprint, session, flash, redirect, url_for
from models.User import User
from services.email_service import send_verification_email
from models import db
from datetime import datetime

email_bp = Blueprint('email', __name__, url_prefix='/email')

# =========================
# Gửi lại email xác nhận
# =========================
@email_bp.route('/resend_verification')
def resend_verification():
    user_email = session.get('user_email')
    user = User.query.filter_by(email=user_email).first()
    if user and not user.is_verified:
        send_verification_email(user)
        flash("Đã gửi lại email xác nhận!", "info")
    else:
        flash("Email đã được xác nhận hoặc không tồn tại.", "warning")
    return redirect(url_for('account'))  # hoặc 'profile'

# =========================
# Xác nhận email qua token
# =========================
@email_bp.route('/verify_email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if user:
        user.is_verified = True
        user.email_verified_at = datetime.utcnow()  # lưu thời gian xác nhận
        user.verification_token = None  # xóa token sau khi xác nhận
        db.session.commit()
        flash("Email của bạn đã được xác nhận!", "success")
    else:
        flash("Link xác nhận không hợp lệ hoặc đã hết hạn.", "danger")
    return redirect(url_for('account'))  # hoặc trang login/profile
