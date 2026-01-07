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

    @staticmethod
    def update_password(user_id, new_password):
        """Cập nhật mật khẩu cho user"""
        try:
            user = User.query.get(user_id)
            if user:
                user.password_hash = new_password  # Trong thực tế nên hash password
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Error updating password: {str(e)}")
            return False
        
    @staticmethod
    def update_user_info(user_id, **kwargs):
        """Cập nhật thông tin user"""
        try:
            user = User.query.get(user_id)
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Error updating user info: {str(e)}")
            return False
