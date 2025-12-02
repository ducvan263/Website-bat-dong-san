from models import db
from models.User import User

class UserService:
    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)
    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()
    @staticmethod
    def create_user(name, email=None, phone=None, password_hash=None, role='user'):
        user = User(name=name, email=email, phone=phone, password_hash=password_hash, role=role)
        db.session.add(user)
        db.session.commit()
        return user
    # ... các method khác tương tự
