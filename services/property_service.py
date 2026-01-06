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

    @staticmethod
    def property_to_text(p: Property):
        purpose = "Giá bán" if p.status == "selling" else "Giá thuê"
        price = p.price_vn if p.price else "Chưa rõ"
        type_name = p.property_type.name if p.property_type else "Bất động sản"

        return (
            f"{p.title}. "
            f"Loại hình {type_name}. "
            f"Vị trí {p.address}. "
            f"{purpose} {price}."
        )


    @staticmethod
    def get_latest_properties(limit=10):
        return (
            Property.query
            .order_by(Property.created_at.desc())
            .limit(limit)
            .all()
        )
