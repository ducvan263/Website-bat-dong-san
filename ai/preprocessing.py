import pandas as pd
import numpy as np
import re

# ================================
# LOAD DATA
# ================================
df = pd.read_csv("datasets/dataset_bds_full.csv")

print("Original shape:", df.shape)
print("Columns:", df.columns.tolist())

# ================================
# 0. BỎ 2 CỘT CUỐI BỊ DƯ (, ,)
# ================================
df = df.iloc[:, :-2]
print("After drop extra columns:", df.shape)

# ================================
# 1. BỎ BẢN GHI LÀ DỰ ÁN (FIX TRIỆT ĐỂ)
# ================================
df["Địa chỉ"] = df["Địa chỉ"].astype(str).str.strip()

# Cách an toàn nhất: bắt đầu bằng "Dự án"
df = df[~df["Địa chỉ"].str.startswith(
    ("Dự án", "DỰ ÁN", "dự án")
)]

print("After remove projects:", df.shape)

# ================================
# 2. TRAIN LẠI QUẬN TỪ ĐỊA CHỈ
# ================================
def extract_district(address):
    if pd.isna(address):
        return None

    patterns = [
        r"(Quận\s+[A-Za-zÀ-ỹ0-9\s]+)",
        r"(Huyện\s+[A-Za-zÀ-ỹ0-9\s]+)",
        r"(Thủ Đức)",
        r"(Thành phố\s+[A-Za-zÀ-ỹ0-9\s]+)"
    ]

    for p in patterns:
        m = re.search(p, address)
        if m:
            return m.group(1).strip()

    return None

df["Quận"] = df["Quận"].fillna(
    df["Địa chỉ"].apply(extract_district)
)

# ================================
# 3. CHUẨN HOÁ TEXT
# ================================
text_cols = [
    "Địa chỉ", "Quận", "Huyện",
    "Loại hình nhà ở", "Giấy tờ pháp lý",
    "Tỉnh/Thành phố"
]

for col in text_cols:
    df[col] = df[col].astype(str).str.strip()

# ================================
# 4. ÉP KIỂU SỐ
# ================================
num_cols = [
    "Số tầng", "Số phòng ngủ",
    "Diện tích", "Giá (triệu đồng/m2)"
]

for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ================================
# 5. BỎ DỮ LIỆU RÁC
# ================================
df = df[
    (df["Diện tích"] > 10) &
    (df["Giá (triệu đồng/m2)"] > 1)
]

#bỏ các tỉnh/thành phố có bản ghi < 300
city_counts = df["Tỉnh/Thành phố"].value_counts()
small_cities = city_counts[city_counts < 300]
cities_to_remove = small_cities.index.tolist()
print("Loại bỏ các tỉnh:", cities_to_remove)
# Lọc dataset
df = df[~df["Tỉnh/Thành phố"].isin(cities_to_remove)]
print("Final shape:", df.shape)

# ================================
# SAVE
# ================================
df.to_csv(
    "models/housing_cleaned.csv",
    index=False,
    encoding="utf-8-sig"
)
