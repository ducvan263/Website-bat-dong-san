from models.Property import Property
from models import db

class PropertyService:
    @staticmethod
    def get_property_by_id(property_id):
        return Property.query.get(property_id)
    @staticmethod
    def get_all_property():
        return Property.query.all()
    @staticmethod
    def get_properties_paginated(page=1, per_page=6):
        query = Property.query.order_by(Property.created_at.desc())

        total = query.count()  # tổng số bản ghi
        properties = query.offset((page - 1) * per_page).limit(per_page).all()

        total_pages = (total + per_page - 1) // per_page

        return {
            "items": properties,
            "total": total,
            "total_pages": total_pages,
            "current_page": page
        }

