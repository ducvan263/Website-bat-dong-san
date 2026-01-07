from datetime import datetime
from models import db
from models.User import User
from models.PropertyImage import PropertyImage

class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('property_types.id'))
    property_type = db.relationship('PropertyType', lazy='joined')
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

    images = db.relationship(
        PropertyImage,  # ✅ class thật
        backref="property",
        cascade="all, delete-orphan",
        order_by=PropertyImage.sort_order
    )
    user = db.relationship(
        User,
        lazy='joined',
    )
    @property
    def price_vn(self):
        if self.price is None:
            return ""

        price = self.price

        if price >= 1_000_000_000:
            return f"{price / 1_000_000_000:.1f} tỷ".rstrip("0").rstrip(".")
        elif price >= 1_000_000:
            return f"{price / 1_000_000:.0f} triệu"
        elif price > 1 :
            return f"{price:,}"
        return "Thỏa thuận"

