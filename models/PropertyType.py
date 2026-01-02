from . import db

class PropertyType(db.Model):
    __tablename__ = "property_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True)

    properties = db.relationship(
        "Property",
        backref="type",
        lazy=True
    )
