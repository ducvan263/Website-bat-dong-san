from sqlalchemy import join

from models import db
from models.Property import Property
from models.Transaction import Transaction
from models.User import User
from models.UserPackage import UserPackage

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
    @staticmethod
    def create_user(name, email=None, phone=None, password_hash=None, role='user'):
        user = User(name=name, email=email, phone=phone, password_hash=password_hash, role=role)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_profile(user_id, name, email, company, phone=None):
        user = User.query.get(user_id)
        if user:
            user.name = name
            user.email = email
            user.company = company
            if phone:
                user.phone = phone
            db.session.commit()
            return user
        return None

    @staticmethod
    def change_password(user_id, current_password, new_password):
        user = User.query.get(user_id)
        if not user:
            return False, "Người dùng không tồn tại"

        # Kiểm tra mật khẩu hiện tại
        if user.password_hash != current_password:
            return False, "Mật khẩu hiện tại không đúng"

        # Cập nhật mật khẩu mới
        user.password_hash = new_password
        db.session.commit()

        return True, "Đổi mật khẩu thành công"

    @staticmethod
    def get_transaction_by_user(user_id):
        rows = db.session.query(Transaction).filter(Transaction.user_id == user_id).all()
        return rows

