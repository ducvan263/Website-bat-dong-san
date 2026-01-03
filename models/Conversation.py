from models import db
from datetime import datetime
from models.Message import Message   # ✅ IMPORT RÕ RÀNG

class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship(
        Message,   # ✅ dùng class
        backref="conversation",
        cascade="all, delete-orphan",
        order_by=Message.created_at
    )
    def __str__(self):
        return str(self.created_by)

    def __repr__(self):
        return str(self.messages)
