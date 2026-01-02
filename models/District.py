from . import db

class District(db.Model):
    __tablename__ = "districts"

    id = db.Column(db.Integer, primary_key=True)
    province_id = db.Column(db.Integer, db.ForeignKey("provinces.id"))
    name = db.Column(db.String(100))
    code = db.Column(db.String(10))
