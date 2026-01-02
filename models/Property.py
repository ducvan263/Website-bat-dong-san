from datetime import datetime
from . import db  # import db từ models/__init__.py

class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('property_types.id'))
    title = db.Column(db.String(150), nullable=False)
    thumbnail = db.Column(db.String())
    price = db.Column(db.Float())
    address = db.Column(db.String(255))
    status = db.Column(db.Enum('selling','sold','renting','rented','hidden'), default='selling')
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'))
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'))
    ward_id = db.Column(db.Integer, db.ForeignKey('wards.id'))
    lat = db.Column(db.Float,default=0.0)
    lng = db.Column(db.Float,default=0.0)
    views = db.Column(db.Integer,default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def price_vn(self):
        if self.price is None:
            return ""

        price = self.price

        if price >= 1_000_000_000:
            return f"{price / 1_000_000_000:.1f} tỷ".rstrip("0").rstrip(".")
        elif price >= 1_000_000:
            return f"{price / 1_000_000:.0f} triệu"
        else:
            return f"{price:,}"

    def __repr__(self):
        return f"<Property {self.title}>"
