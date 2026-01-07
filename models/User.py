from datetime import datetime
from . import db  # import db từ models/__init__.py

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(30))
    password_hash = db.Column(db.String(255))
    role = db.Column(db.Enum('user','agent','admin'), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 23130071 thêm vào
    is_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    company = db.Column(db.String(255), nullable=True)
    def __repr__(self):
        return f"<User {self.name}>"