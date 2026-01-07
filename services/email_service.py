import secrets
from flask import current_app
from flask_mail import Message
from models import db
from models.User import User

def generate_verification_token():
    """Tạo token xác thực ngẫu nhiên"""
    return secrets.token_urlsafe(32)

def send_verification_email(user):
    """
    Gửi email xác nhận đến user.
    Sử dụng current_app để lấy mail từ app factory.
    """
    token = generate_verification_token()
    user.verification_token = token
    db.session.commit()

    # Lấy mail object từ current_app
    mail = current_app.extensions.get('mail')
    if not mail:
        raise RuntimeError("Flask-Mail chưa được khởi tạo!")

    # Lấy URL base app từ request context
    from flask import request
    app_url = request.host_url.rstrip('/')  # ví dụ: http://localhost:5000

    verify_url = f"{app_url}/email/verify_email/{token}"

    msg = Message(
        subject="Xác nhận email",
        sender=current_app.config.get('MAIL_USERNAME'),
        recipients=[user.email],
        body=f"Xin chào {user.email},\n\n"
             f"Vui lòng nhấp vào link sau để xác nhận email:\n{verify_url}\n\nCảm ơn!"
    )

    mail.send(msg)
