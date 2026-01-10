from datetime import datetime
from . import db

class UserPackage(db.Model):
    __tablename__ = 'user_packages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    package_key = db.Column(db.String(50), nullable=False)  # single, week, vip
    post_limit = db.Column(db.Integer, default=0)           # số lượt đăng còn lại
    package_expired_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reset = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref=db.backref("packages", lazy=True))

    def __repr__(self):
        return f"<UserPackage user_id={self.user_id} package={self.package_key} posts_left={self.post_limit}>"
