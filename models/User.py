from datetime import datetime

from . import db  # import db từ models/__init__.py
from models.UserPackage import UserPackage
from models.UserFreeQuota import UserFreeQuota

PACKAGES = {
    "single": {"name": "1 tin / 3 ngày", "price": 15000, "limit": 1, "days": 1, "post_expire_days": 3},
    "week": {"name": "7 ngày", "price": 59000, "limit": 5, "days": 7, "post_expire_days": 7},
    "vip": {"name": "VIP 30 ngày", "price": 199000, "limit": -1, "days": 30, "post_expire_days": 30},
}
DEFAULT_FREE_POSTS_PER_DAY = 1

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
    avatar = db.Column(db.String(255), nullable=True)
    # ===== EMAIL VERIFY =====
    is_email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    verification_token = db.Column(db.String(100), nullable=True)

    # ===== PHONE VERIFY =====
    is_phone_verified = db.Column(db.Boolean, default=False)
    phone_verified_at = db.Column(db.DateTime, nullable=True)

    phone_otp = db.Column(db.String(6), nullable=True)
    phone_otp_expires = db.Column(db.DateTime, nullable=True)


    reset_password_token = db.Column(db.String(100), nullable=True)
    reset_password_expires = db.Column(db.DateTime, nullable=True)

    package = db.relationship(UserPackage, lazy='joined')


    def __repr__(self):
        return f"<User {self.is_email_verified}>"

    def get_active_package(self):
        now = datetime.utcnow()
        return UserPackage.query.filter(
            UserPackage.user_id == self.id,
            UserPackage.package_expired_at > now
        ).order_by(UserPackage.created_at.desc()).first()

    def get_today_post_limit(self):
        now = datetime.utcnow()
        active_pkg = self.get_active_package()

        # ===== USER CÓ GÓI =====
        if active_pkg:
            if not active_pkg.last_reset or active_pkg.last_reset.date() < now.date():
                active_pkg.post_limit = PACKAGES[active_pkg.package_key]["limit"]
                active_pkg.last_reset = now
                db.session.commit()

            return active_pkg.post_limit

        # ===== USER FREE =====
        quota = UserFreeQuota.query.filter_by(
            user_id=self.id,
            date=now.date()
        ).first()

        used = quota.used if quota else 0
        return max(0, DEFAULT_FREE_POSTS_PER_DAY - used)

    def reduce_post_limit(self):
        now = datetime.utcnow()
        active_pkg = self.get_active_package()

        # ===== USER CÓ GÓI =====
        if active_pkg:
            if not active_pkg.last_reset or active_pkg.last_reset.date() < now.date():
                active_pkg.post_limit = PACKAGES[active_pkg.package_key]["limit"]
                active_pkg.last_reset = now

            if active_pkg.post_limit > 0:
                active_pkg.post_limit -= 1

            db.session.commit()
            return

        # ===== USER FREE =====
        quota = UserFreeQuota.query.filter_by(
            user_id=self.id,
            date=now.date()
        ).first()

        if not quota:
            quota = UserFreeQuota(
                user_id=self.id,
                date=now.date(),
                used=0
            )
            db.session.add(quota)

        quota.used += 1
        db.session.commit()
