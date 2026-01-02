# TRAIN + PREDICT GIÁ NHÀ HÀ NỘI
# - Có feature QUẬN + PHƯỜNG (hierarchical)
# - RandomForestRegressor

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings("ignore")

# -------------------------
# 1. LOAD DATA (JSON LINES)
# -------------------------
DATA_FILE = "datasets/data_hn.json"
MODEL_FILE = "models/hanoi/rf_price_hanoi_v2.joblib"

# mỗi dòng là 1 JSON object
df = pd.read_json(DATA_FILE, lines=True)

# -------------------------
# 2. CLEAN DATA
# -------------------------
# bỏ bản ghi thiếu giá
df = df[df["Giá (triệu đồng/m2)"].notna()].reset_index(drop=True)

# target: VNĐ/m²
df["price_per_m2"] = df["Giá (triệu đồng/m2)"] * 1_000_000

# -------------------------
# 3. ENCODE FEATURE
# -------------------------
le_type = LabelEncoder()
le_district = LabelEncoder()
le_ward = LabelEncoder()

# encode categorical cơ bản
df["house_type"] = le_type.fit_transform(
    df["Loại hình nhà ở"].fillna("Unknown")
)

df["district"] = le_district.fit_transform(
    df["Quận"].fillna("Unknown")
)

# -------------------------
# 4. FEATURE PHƯỜNG (HIERARCHICAL)
# -------------------------
# dùng Huyện như phường (theo dataset của bạn)
df["ward"] = df["Huyện"].fillna("Unknown")

# ghép Quận + Phường để tránh trùng tên
df["ward_full"] = df["Quận"] + "_" + df["ward"]

# gộp phường hiếm (<20 mẫu)
ward_counts = df["ward_full"].value_counts()
rare_wards = ward_counts[ward_counts < 20].index

df.loc[df["ward_full"].isin(rare_wards), "ward_full"] = "Other"

df["ward_code"] = le_ward.fit_transform(df["ward_full"])

# -------------------------
# 5. DATASET
# -------------------------
FEATURES = [
    "Diện tích",
    "Số tầng",
    "Số phòng ngủ",
    "house_type",
    "district",
    "ward_code"
]

X = df[FEATURES]
y = np.log1p(df["price_per_m2"])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -------------------------
# 6. TRAIN / TEST
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

rf = RandomForestRegressor(
    n_estimators=350,
    max_depth=18,
    min_samples_leaf=3,
    random_state=42,
    n_jobs=-1
)

rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

rmse = np.sqrt(mean_squared_error(
    np.expm1(y_test),
    np.expm1(y_pred)
))

print(f"RMSE Hà Nội VNĐ/m²: {rmse:,.0f}")

# -------------------------
# 7. SAVE MODEL
# -------------------------
joblib.dump(rf, MODEL_FILE)
joblib.dump(scaler, "models/hanoi/scaler_hanoi_v2.joblib")
joblib.dump(le_type, "models/hanoi/le_type_hanoi_v2.joblib")
joblib.dump(le_district, "models/hanoi/le_district_hanoi_v2.joblib")
joblib.dump(le_ward, "models/hanoi/le_ward_hanoi_v2.joblib")


print("Saved Hanoi model v2 (with ward)")

# -------------------------
# 8. PREDICT FUNCTION
# -------------------------

def predict_price(sample: dict):
    """
    sample = {
      'Diện tích': 46.0,
      'Số tầng': 4,
      'Số phòng ngủ': 5,
      'Loại hình nhà ở': 'Nhà ngõ, hẻm',
      'Quận': 'Quận Cầu Giấy',
      'Huyện': 'Phường Nghĩa Đô'
    }
    """

    ward_full = sample["Quận"] + "_" + sample.get("Huyện", "Unknown")
    if ward_full not in le_ward.classes_:
        ward_full = "Other"

    X_new = scaler.transform([[
        sample["Diện tích"],
        sample["Số tầng"],
        sample["Số phòng ngủ"],
        le_type.transform([sample["Loại hình nhà ở"]])[0],
        le_district.transform([sample["Quận"]])[0],
        le_ward.transform([ward_full])[0]
    ]])

    log_price = rf.predict(X_new)[0]
    return np.expm1(log_price)

# -------------------------
# 9. TEST NHANH
# -------------------------
if __name__ == '__main__':
    sample = {
        "Diện tích": 46.0,
        "Số tầng": 4,
        "Số phòng ngủ": 5,
        "Loại hình nhà ở": "Nhà ngõ, hẻm",
        "Quận": "Quận Hai Bà Trưng",
        "Huyện": "Phường Minh Khai"
    }

    pred = predict_price(sample)
    print("===== TEST HÀ NỘI  =====")
    print(f"Giá dự đoán: {pred:,.0f} VNĐ/m²")
