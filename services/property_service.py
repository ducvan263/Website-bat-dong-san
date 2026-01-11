from models.District import District
from models.Property import Property
import uuid,os
from flask import current_app
from werkzeug.utils import secure_filename

from models.PropertyAttribute import PropertyAttribute
from models.PropertyDetail import PropertyDetail
from models.PropertyImage import PropertyImage
from models.Province import Province
from models.Ward import Ward
from models import db

class PropertyService:
    @staticmethod
    def get_property_by_id(property_id):
        return Property.query.get(property_id)
    @staticmethod
    def get_all_property():
        return Property.query.all()
    @staticmethod
    def get_property_by_user_id(user_id):
        return Property.query.filter_by(user_id=user_id).all()
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

    @staticmethod
    def save_property_image(file, property_id, index):
        """
        index: số thứ tự ảnh (bắt đầu từ 1)
        """
        if not file:
            return None

        ext = os.path.splitext(secure_filename(file.filename))[1].lower()
        filename = f"img_{index}{ext}"

        upload_dir = os.path.join(
            current_app.root_path,
            "static",
            "img",
            "property_images",
            str(property_id)
        )
        os.makedirs(upload_dir, exist_ok=True)

        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        return f"img/property_images/{property_id}/{filename}"
    @staticmethod
    def normalize_province_name(province_name: str):
        if not province_name:
            return province_name

        province_name = province_name.strip()

        if province_name.lower().startswith("thành phố"):
            return province_name.replace("Thành phố", "", 1).strip()

        return province_name

    @staticmethod
    def _get_location_ids(province_name, district_name, ward_name):
        province = Province.query.filter_by(name=PropertyService.normalize_province_name(province_name)).first()
        district = District.query.filter_by(name=district_name).first()
        ward = Ward.query.filter_by(name=ward_name).first()

        return (
            province.id if province else None,
            district.id if district else None,
            ward.id if ward else None
        )

    @staticmethod
    def create_property(form, files, user_id):
        # 1. map location
        province_id, district_id, ward_id = PropertyService._get_location_ids(
            form.get("province"),
            form.get("district"),
            form.get("ward")
        )

        # 2. tạo property trước
        prop = Property(
            user_id=user_id,
            title=form.get("title"),
            price=form.get("price"),
            address=form.get("city"),
            province_id=province_id,
            district_id=district_id,
            ward_id=ward_id,
            status="selling"
        )

        db.session.add(prop)
        db.session.flush()  # ⚠ lấy prop.id ngay

        # 3 + 6. thumbnail + gallery images (gộp chung)
        images = []

        thumbnail = files.get("thumbnail")
        if thumbnail:
            images.append(thumbnail)

        gallery_images = files.getlist("images[]")
        images.extend(gallery_images)

        for index, img in enumerate(images, start=1):
            img_url = PropertyService.save_property_image(img, prop.id, index)

            # img_1 là thumbnail
            if index == 1:
                prop.thumbnail = img_url

            db.session.add(PropertyImage(
                property_id=prop.id,
                url=img_url,
                is_featured=1 if index == 1 else 0,
                sort_order=index
            ))

        # 4. attributes
        db.session.add(PropertyAttribute(
            property_id=prop.id,
            area=form.get("Diện tích"),
            bedrooms=form.get("Số phòng ngủ"),
            floor=form.get("Số tầng"),
            legal_status=form.get("Giấy tờ pháp lý")
        ))

        # 5. details
        db.session.add(PropertyDetail(
            property_id=prop.id,
            overview=prop.title,
            full_address=f"{form.get('ward')}, {form.get('district')}, {form.get('province')}"
        ))

        db.session.commit()
        return prop
