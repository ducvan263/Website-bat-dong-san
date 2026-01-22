from . import db
from datetime import datetime


SENTIMENT_MAP = {
    "Negative": 0,
    "Neutral": 1,
    "Positive": 2,
    "Spam": 3
}
class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sentiment_label = db.Column(db.Integer, nullable=False)
    user = db.relationship("User", backref="reviews")
    def __repr__(self):
        return "<Review %r>" % self.id

    def format_created(self):
        now = datetime.utcnow()
        diff = now - self.created_at  # timedelta

        seconds = diff.total_seconds()
        minutes = seconds // 60
        hours = seconds // 3600
        days = diff.days

        if seconds < 60:
            return "Vừa xong"
        elif minutes < 60:
            return f"{int(minutes)} phút trước"
        elif hours < 24:
            return f"{int(hours)} giờ trước"
        elif days < 7:
            return f"{int(days)} ngày trước"
        elif days < 30:
            weeks = days // 7
            return f"{int(weeks)} tuần trước"
        elif days < 365:
            months = days // 30
            return f"{int(months)} tháng trước"
        else:
            years = days // 365
            return f"{int(years)} năm trước"