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

    def property_to_text(p: Property, include_private=False):
        text = (
            f"{p.title}. "
            f"Loại hình {p.property_type.name if p.property_type else 'BĐS'}. "
            f"Vị trí {p.address}. "
            f"Giá {p.price_vn}. "
        )

        if include_private:
            contact = []
            if p.user:
                if p.user.phone:
                    contact.append(f"SĐT: {p.user.phone}")
                if p.user.email:
                    contact.append(f"Email: {p.user.email}")

            link = f"http://127.0.0.1:5000/property/{p.id}"
            text += "Liên hệ: " + ", ".join(contact) + ". "
            text += f"Link chi tiết: {link}."

        return text

    @staticmethod
    def get_latest_properties(limit=10):
        return (
            Property.query
            .order_by(Property.created_at.desc())
            .limit(limit)
            .all()
        )
