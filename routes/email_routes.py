from flask import Blueprint, redirect, flash
from services.email_service import verify_token
from models.User import User
from app import db
from datetime import datetime

email_bp = Blueprint('email', __name__)

@email_bp.route('/verify-email/<token>')
def verify_email(token):
    email = verify_token(token)
    if not email:
        return "Link không hợp lệ hoặc đã hết hạn"

    user = User.query.filter_by(email=email).first()
    if not user:
        return "User không tồn tại"

    user.is_verified = True
    user.email_verified_at = datetime.utcnow()
    db.session.commit()

    return "Xác thực email thành công"
