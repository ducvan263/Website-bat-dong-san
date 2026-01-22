import secrets
from flask import current_app,request
from flask_mail import Message
from models import db
from models.User import User
from datetime import datetime, timedelta


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
def send_reset_password_email(user):
    token = generate_verification_token()

    user.reset_password_token = token
    user.reset_password_expires = datetime.utcnow() + timedelta(minutes=15)
    db.session.commit()

    mail = current_app.extensions.get('mail')

    app_url = request.host_url.rstrip('/')
    reset_url = f"{app_url}/reset-password/{token}"

    msg = Message(
        subject="Đặt lại mật khẩu",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.email],
        body=f"""
Xin chào {user.email},

Bạn đã yêu cầu đặt lại mật khẩu.
Vui lòng click link bên dưới (có hiệu lực 15 phút):

{reset_url}

Nếu không phải bạn yêu cầu, hãy bỏ qua email này.
"""
    )

    mail.send(msg)

def send_property_negative_notice(property_obj, action="hidden"):
    """
    action: 'hidden' | 'deleted'
    """
    mail = current_app.extensions.get('mail')
    if not mail:
        raise RuntimeError("Flask-Mail chưa được khởi tạo!")

    app_url = request.host_url.rstrip('/')
    property_url = f"{app_url}/property/{property_obj.id}"

    if action == "hidden":
        subject = "Bài đăng của bạn đã bị ẩn do nhiều bình luận tiêu cực"
        action_text = "đã bị ẩn tạm thời"
    else:
        subject = "Bài đăng của bạn đã bị xóa do vi phạm chất lượng"
        action_text = "đã bị xóa"

    msg = Message(
        subject=subject,
        sender=current_app.config.get('MAIL_USERNAME'),
        recipients=[property_obj.user.email],
        body=f"""
Xin chào {property_obj.user.email},

Bài đăng: "{property_obj.title}"
{action_text} do nhận được nhiều bình luận tiêu cực từ người dùng.

Link bài đăng:
{property_url}

Nếu bạn cho rằng đây là nhầm lẫn, vui lòng liên hệ với bộ phận quản trị để được hỗ trợ.

Trân trọng,
Ban quản trị hệ thống
"""
    )

    mail.send(msg)
