from . import db


class PropertyAttribute(db.Model):
    __tablename__ = "property_attributes"
    property_id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.Float)
