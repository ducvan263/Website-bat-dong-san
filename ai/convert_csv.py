import pandas as pd
import numpy as np
import re

# ==========================
# 1. ĐỌC DATASET
# ==========================
df1 = pd.read_csv(
    "datasets/chotot_data.csv",
    encoding="utf-8-sig",
    sep=None,
    engine="python"
)

# Chuẩn hóa tên cột
df1.columns = df1.columns.str.strip()

# ==========================
# 2. HÀM XỬ LÝ CHUNG
# ==========================
def clean_numeric(val):
    if pd.isna(val):
        return np.nan

    val = str(val).lower()
    if "giá tốt" in val:
        return np.nan

    nums = re.findall(r"\d+", val.replace(".", ""))
    return float(nums[0]) if nums else np.nan


def parse_price_m2(val):
    if pd.isna(val):
        return np.nan

    val = str(val).lower()
    num = clean_numeric(val)

    if num is None:
        return np.nan

    if "tỷ" in val:
        return num * 1000   # tỷ → triệu

    if "đ" in val:
        return num / 1_000_000  # đồng → triệu

    return num


# ==========================
# 3. TRÍCH SỐ TẦNG (ĐÚNG)
# ==========================
def extract_floors(text):
    if pd.isna(text):
        return np.nan

    text = str(text).lower()

    patterns = [
        r'(\d+)\s*tầng',
        r'(\d+)\s*lầu',
        r'(\d+)t\b',
        r'nhà\s*cấp\s*(\d+)'
    ]

    for p in patterns:
        m = re.search(p, text)
        if m:
            return float(m.group(1))

    return np.nan


# ==========================
# 4. TRÍCH SỐ PHÒNG NGỦ (ĐÚNG)
# ==========================
def extract_bedrooms(text):
    if pd.isna(text):
        return np.nan

    text = str(text).lower()

    # Loại các trường hợp không phải nhà ở
    ignore_patterns = [
        r'phòng trọ',
        r'khu trọ',
        r'nhà trọ',
        r'nhiều hơn \d+ phòng'
    ]

    for p in ignore_patterns:
        if re.search(p, text):
            return np.nan

    patterns = [
        r'(\d+)\s*phòng ngủ',
        r'(\d+)\s*pn\b',
        r'(\d+)\s*phòng\b'
    ]

    for p in patterns:
        m = re.search(p, text)
        if m:
            return float(m.group(1))

    return np.nan


# ==========================
# 5. TÁCH QUẬN / PHƯỜNG
# ==========================
def extract_location(addr):
    if pd.isna(addr):
        return pd.Series([np.nan, np.nan])

    parts = [p.strip() for p in str(addr).split(",")]

    quan = next((p for p in parts if "Quận" in p or "Huyện" in p), np.nan)
    phuong = next((p for p in parts if "Phường" in p or "Xã" in p), np.nan)

    return pd.Series([quan, phuong])


# ==========================
# 6. GỘP TEXT ĐỂ NLP
# ==========================
df1["text_all"] = (
    df1.get("title", "").astype(str) + " " +
    df1.get("description", "").astype(str)
)

# ==========================
# 7. TẠO DATASET CHUẨN
# ==========================
df_final = pd.DataFrame()

df_final["Ngày"] = pd.Timestamp.now().strftime("%d/%m/%Y")
df_final["Địa chỉ"] = df1.get("location", np.nan)

df_final[["Quận", "Phường"]] = df_final["Địa chỉ"].apply(extract_location)

df_final["Loại hình"] = df1.get("Loại hình nhà ở:", df1.get("Loại hình đất:", np.nan))
df_final["Pháp lý"] = df1.get("Giấy tờ pháp lý:", np.nan)

df_final["Số tầng"] = df1["text_all"].apply(extract_floors)
df_final["Số phòng ngủ"] = df1["text_all"].apply(extract_bedrooms)

df_final["Diện tích"] = df1.get("Diện tích đất:", np.nan).apply(clean_numeric)
df_final["Dài"] = df1.get("Chiều dài:", np.nan).apply(clean_numeric)
df_final["Rộng"] = df1.get("Chiều ngang:", np.nan).apply(clean_numeric)

df_final["Giá/m2"] = df1.get("Giá/m2:", np.nan).apply(parse_price_m2)

# ==========================
# 8. LỌC DỮ LIỆU RÁC (NÊN CÓ)
# ==========================
df_final = df_final[
    (df_final["Diện tích"] > 10) &
    (df_final["Giá/m2"] > 1)
]

# ==========================
# 9. XUẤT FILE
# ==========================
df_final.to_csv(
    "dataset_chotot_cleaned.csv",
    index=False,
    encoding="utf-8-sig"
)

print("✅ CLEAN DATA THÀNH CÔNG")
print(df_final.head())
