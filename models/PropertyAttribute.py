from datetime import datetime
from . import db
from .Property import Property


class PropertyAttribute(db.Model):
    __tablename__ = "property_attributes"

    # PK + FK (1-1 với properties)
    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id", ondelete="CASCADE"),
        primary_key=True
    )

    area = db.Column(db.Float)
    bedrooms = db.Column(db.SmallInteger)
    bathrooms = db.Column(db.SmallInteger)
    floor = db.Column(db.Integer)
    direction = db.Column(db.String(50))
    legal_status = db.Column(db.String(100))
    year_built = db.Column(db.SmallInteger)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # relationship
    property = db.relationship(
        Property,
        backref=db.backref(
            "attributes",
            uselist=False,
            cascade="all, delete-orphan"
        )
    )

    def __repr__(self):
        return f"<PropertyAttribute property_id={self.property_id}>"
