from datetime import datetime
from . import db
from .Property import Property


class PropertyDetail(db.Model):
    __tablename__ = "property_details"

    # PK + FK (1-1)
    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id", ondelete="CASCADE"),
        primary_key=True
    )

    overview = db.Column(db.Text)
    utilities = db.Column(db.Text)
    full_address = db.Column(db.String(255))

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
            "details",
            uselist=False,
            cascade="all, delete-orphan"
        )
    )

    def __repr__(self):
        return f"<PropertyDetail property_id={self.property_id}>"
