from . import db
from datetime import datetime



class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    package = db.Column(db.String(50))
    amount = db.Column(db.Integer)
    payment_method = db.Column(db.String(20))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

