from datetime import datetime
from . import db

class ReviewReport(db.Model):
    __tablename__ = 'review_reports'

    id = db.Column(db.Integer, primary_key=True)

    review_id = db.Column(db.Integer, nullable=False)
    reporter_id = db.Column(db.Integer, nullable=False)

    reason = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


