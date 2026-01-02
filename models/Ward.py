from . import db

class Ward(db.Model):
    __tablename__ = "wards"

    id = db.Column(db.Integer, primary_key=True)
    district_id = db.Column(db.Integer, db.ForeignKey("districts.id"))
    name = db.Column(db.String(100))
    code = db.Column(db.String(10))
