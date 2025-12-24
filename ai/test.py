# import pandas as pd
#
# df = pd.read_csv("models/housing_cleaned.csv")
#
# city_counts = df["Tỉnh/Thành phố"].value_counts()
#
# print(city_counts)

import joblib
import numpy as np

# Load một lần duy nhất khi chạy chương trình
MODEL_PATH = "models/hanoi/"
rf = joblib.load(MODEL_PATH + "rf_price_hanoi_v2.joblib")
scaler = joblib.load(MODEL_PATH + "scaler_hanoi_v2.joblib")
le_type = joblib.load(MODEL_PATH + "le_type_hanoi_v2.joblib")
le_district = joblib.load(MODEL_PATH + "le_district_hanoi_v2.joblib")
le_ward = joblib.load(MODEL_PATH + "le_ward_hanoi_v2.joblib")


def predict_price(sample: dict):
    # Xử lý Ward Hierarchical
    ward_full = sample["Quận"] + "_" + sample.get("Huyện", "Unknown")

    # Kiểm tra xem ward này có trong bộ từ điển lúc train không
    if ward_full not in le_ward.classes_:
        ward_full = "Other"

    # Encode các giá trị text
    try:
        type_code = le_type.transform([sample["Loại hình nhà ở"]])[0]
        dist_code = le_district.transform([sample["Quận"]])[0]
        ward_code = le_ward.transform([ward_full])[0]
    except ValueError as e:
        # Trường hợp gặp Quận hoặc Loại nhà hoàn toàn mới
        print(f"Lỗi: Dữ liệu đầu vào chưa được học ({e})")
        return None

    # Tạo vector input và scale
    features = [[
        sample["Diện tích"],
        sample["Số tầng"],
        sample["Số phòng ngủ"],
        type_code,
        dist_code,
        ward_code
    ]]

    X_new = scaler.transform(features)
    log_price = rf.predict(X_new)[0]

    return np.expm1(log_price)


# --- TEST NHANH ---
if __name__ == '__main__':
    my_house = {
        "Diện tích": 46.0,
        "Số tầng": 4,
        "Số phòng ngủ": 5,
        "Loại hình nhà ở": "Nhà ngõ, hẻm",
        "Quận": "Quận Hai Bà Trưng",
        "Huyện": "Phường Minh Khai"
    }

    result = predict_price(my_house)
    if result:
        print(f"Giá dự đoán: {result:,.0f} VNĐ/m²")
        print(f"Tổng giá trị căn nhà: {(result * my_house['Diện tích']):,.0f} VNĐ")