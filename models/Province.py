from . import db

class Province(db.Model):
    __tablename__ = "provinces"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10))

    properties = db.relationship(
        "Property",
        backref="province",
        lazy=True
    )
