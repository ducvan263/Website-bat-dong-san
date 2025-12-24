import pandas as pd
import re
from datetime import date

# ==============================
# CONFIG
# ==============================
INPUT_CSV = "datasets/vietnam_housing_dataset.csv"        # file CSV gốc
OUTPUT_CSV = "real_estate_standardized.csv"  # file CSV sau xử lý


# ==============================
# HELPER FUNCTIONS
# ==============================
def map_legal(x):
    if pd.isna(x):
        return None
    x = x.lower()
    if "certificate" in x:
        return "Đã có sổ"
    if "sale" in x:
        return "Hợp đồng mua bán"
    return None


def map_type(address):
    if pd.isna(address):
        return None
    address = address.lower()
    if "dự án" in address:
        return "Nhà phố liền kề"
    if "đường" in address:
        return "Nhà mặt phố, mặt tiền"
    return None


def extract_ward(address):
    if pd.isna(address):
        return None
    m = re.search(r'Phường\s[^,]+', address)
    return m.group(0) if m else None


HCM_URBAN_DISTRICTS = [
    "Gò Vấp", "Tân Bình", "Tân Phú", "Bình Thạnh", "Phú Nhuận",
    "Bình Tân", "Quận 1", "Quận 3", "Quận 4", "Quận 5",
    "Quận 6", "Quận 7", "Quận 8", "Quận 10", "Quận 11",
    "Quận 12", "Thủ Đức"
]

def extract_district(address):
    if pd.isna(address):
        return None

    # 1️⃣ Regex chuẩn: Quận / Huyện / Thành phố
    m = re.search(r'(Quận|Huyện|Thành phố)\s[^,]+', address)
    if m:
        return m.group(0)

    # 2️⃣ Fallback cho TP.HCM (không có chữ "Quận")
    for d in HCM_URBAN_DISTRICTS:
        if d.lower() in address.lower():
            if d.startswith("Quận"):
                return d
            return f"Quận {d}"

    return None


# ==============================
# MAIN
# ==============================
def main():
    # Load CSV gốc
    df = pd.read_csv(INPUT_CSV)

    # Chuẩn hóa kiểu số
    for col in ["Area", "Frontage", "Access Road", "Floors", "Bedrooms", "Price"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Tạo dataset mới
    new_df = pd.DataFrame({
        "Ngày": date.today().isoformat(),
        "Địa chỉ": df["Address"],
        "Quận": df["Address"].apply(extract_district),
        "Phường": df["Address"].apply(extract_ward),
        "Loại hình": df["Address"].apply(map_type),
        "Pháp lý": df["Legal status"].apply(map_legal),
        "Số tầng": df.get("Floors"),
        "Số phòng ngủ": df.get("Bedrooms"),
        "Diện tích": df.get("Area"),
        "Dài": df.get("Access Road"),
        "Rộng": df.get("Frontage"),
        "Giá/m2": (df["Price"] * 1000) / df["Area"]  # Price giả định là tỷ
    })

    # Lưu CSV
    new_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"✅ Done! File saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
