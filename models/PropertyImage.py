from datetime import datetime
from models import db

class PropertyImage(db.Model):
    __tablename__ = 'property_images'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'))
    url = db.Column(db.String(500), nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
