from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from flask_mail import Message
from app import mail

def generate_verify_token(email):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt='email-verify')

def verify_token(token, expiration=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='email-verify', max_age=expiration)
        return email
    except:
        return None

def send_verify_email(user):
    token = generate_verify_token(user.email)
    link = f"http://localhost:5000/verify-email/{token}"

    msg = Message(
        "Xác thực email",
        recipients=[user.email],
        body=f"Bấm vào link để xác thực email: {link}"
    )
    mail.send(msg)

