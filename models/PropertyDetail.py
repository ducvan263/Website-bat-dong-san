from datetime import datetime
from . import db

class PropertyDetail(db.Model):
    __tablename__ = "property_details"
    property_id = db.Column(db.Integer, primary_key=True)
    utilities = db.Column(db.Text)
