import json
import mysql.connector
import traceback
import os

# --- CẤU HÌNH DATABASE ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'batdongsan',
    'charset': 'utf8mb4'
}


def get_or_create_location(cursor, table, name, parent_id=None, parent_col=None):
    """Tìm ID hoặc tạo mới Tỉnh/Huyện/Xã - Đã xử lý chặn NULL"""
    if not name or str(name).strip() == "" or str(name).lower() == "none":
        return None

    name = str(name).strip()
    query = f"SELECT id FROM {table} WHERE name = %s"
    params = [name]

    if parent_id and parent_col:
        query += f" AND {parent_col} = %s"
        params.append(parent_id)

    cursor.execute(query, tuple(params))
    result = cursor.fetchone()

    if result:
        return result['id']
    else:
        # Thêm mới nếu chưa có
        if parent_id and parent_col:
            cursor.execute(f"INSERT INTO {table} (name, {parent_col}) VALUES (%s, %s)", (name, parent_id))
        else:
            cursor.execute(f"INSERT INTO {table} (name) VALUES (%s)", (name,))
        return cursor.lastrowid


def insert_to_db(json_file):
    # Kết nối Database
    try:
        conn = mysql.connector.connect(**db_config)
        # QUAN TRỌNG: buffered=True để tránh lỗi "Unread result found"
        cursor = conn.cursor(dictionary=True, buffered=True)
    except Exception as e:
        print(f"❌ Không thể kết nối Database: {e}")
        return

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            properties_data = json.load(f)

        for item in properties_data:
            # 1. Xử lý User (Đảm bảo không bao giờ NULL name)
            phone = str(item.get('user_phone') or "").strip()
            user_name = str(item.get('user_name') or "Người dùng ẩn danh").strip()

            cursor.execute("SELECT id FROM users WHERE phone = %s", (phone,))
            user = cursor.fetchone()

            if not user:
                cursor.execute("INSERT INTO users (name, phone, role) VALUES (%s, %s, 'agent')",
                               (user_name, phone))
                user_id = cursor.lastrowid
            else:
                user_id = user['id']

            # 2. Xử lý Địa giới hành chính
            p_id = get_or_create_location(cursor, 'provinces', item.get('province_name'))
            d_id = get_or_create_location(cursor, 'districts', item.get('district_name'), p_id, 'province_id')
            w_id = get_or_create_location(cursor, 'wards', item.get('ward_name'), d_id, 'district_id')

            # 3. Insert bảng PROPERTIES
            # Dùng INSERT IGNORE để nếu chạy lại bản ghi cũ sẽ không bị báo lỗi trùng
            prop_sql = """
                INSERT INTO properties (user_id, title, thumbnail, price, address, province_id, district_id, ward_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'selling')
            """
            cursor.execute(prop_sql, (
                user_id,
                item.get('title', 'Không tiêu đề'),
                item.get('thumbnail'),
                item.get('price', 0),
                item.get('address_full'),
                p_id, d_id, w_id
            ))
            property_id = cursor.lastrowid

            # 4. Insert bảng PROPERTY_ATTRIBUTES
            attr = item.get('attr', {})
            attr_sql = """
                INSERT INTO property_attributes (property_id, area, bedrooms, bathrooms, floor, direction, legal_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(attr_sql, (
                property_id,
                item.get('area', 0),
                attr.get('bedrooms'),
                attr.get('bathrooms'),
                attr.get('floors'),
                attr.get('direction'),
                attr.get('legal')
            ))

            # 5. Insert bảng PROPERTY_DETAILS
            detail_sql = "INSERT INTO property_details (property_id, overview, full_address) VALUES (%s, %s, %s)"
            cursor.execute(detail_sql, (
                property_id,
                item.get('description', ''),
                item.get('address_full', '')
            ))

            # 6. Insert bảng PROPERTY_IMAGES
            for img_path in item.get('images', []):
                is_feat = 1 if img_path == item.get('thumbnail') else 0
                cursor.execute("INSERT INTO property_images (property_id, url, is_featured) VALUES (%s, %s, %s)",
                               (property_id, img_path, is_feat))

            print(f"✅ Đã nạp: {item.get('title', 'N/A')[:40]}...")

        conn.commit()
        print(f"\n🚀 TẤT CẢ HOÀN TẤT! Đã xử lý {len(properties_data)} bản ghi.")

    except Exception:
        conn.rollback()
        print("❌ LỖI TRONG QUÁ TRÌNH NẠP DỮ LIỆU:")
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    # Đảm bảo file JSON nằm đúng vị trí này
    file_path = '../ai/data/properties_cleaned.json'

    if os.path.exists(file_path):
        insert_to_db(file_path)
    else:
        print(f"❌ Không thấy file: {os.path.abspath(file_path)}")