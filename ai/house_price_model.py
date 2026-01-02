import joblib
import numpy as np
import pandas as pd


class HousePricePredictor:
    def __init__(self):
        # Đường dẫn file cần khớp với thư mục bạn đã lưu
        self.model_hn = joblib.load("ai/models/hanoi/xgboost_hanoi.pkl")
        self.map_hn = joblib.load("ai/models/hanoi/encoding_maps.pkl")

        self.model_others = joblib.load("ai/models/other/xgboost_others_model.pkl")
        self.map_others = joblib.load("ai/models/other/encoding_maps_others.pkl")

    def _encode(self, df, encoding_maps):
        df_encoded = df.copy()
        for col, mapping in encoding_maps.items():
            # Chuyển tên về dạng số dựa trên mapping đã lưu
            df_encoded[col] = df_encoded[col].map(mapping)
            # Nếu gặp giá trị mới (chưa có trong train), lấy giá trị trung bình của cột đó
            if df_encoded[col].isnull().any():
                default_val = np.mean(list(mapping.values()))
                df_encoded[col] = df_encoded[col].fillna(default_val)
        return df_encoded

    def predict(self, data: dict):
        df = pd.DataFrame([data])

        # Kiểm tra tỉnh thành (loại bỏ khoảng trắng và chuẩn hóa)
        province = str(data.get("Tỉnh/Thành phố", "")).strip()

        if province == "Hà Nội":
            # Feature Engineering cho Hà Nội
            df["Total_Floor_Area"] = df["Diện tích"] * df["Số tầng"]
            # Xử lý an toàn cho cột 'Loại hình nhà ở'
            loai_hinh = str(data.get("Loại hình nhà ở", "")).lower()
            df["Is_Mat_Pho"] = 1 if "mặt phố" in loai_hinh else 0

            features = [
                'Quận', 'Phường', 'Loại hình nhà ở', 'Giấy tờ pháp lý',
                'Số tầng', 'Số phòng ngủ', 'Diện tích',
                'Total_Floor_Area', 'Is_Mat_Pho'
            ]

            df_input = self._encode(df, self.map_hn)
            y = self.model_hn.predict(df_input[features])

        else:
            # Model cho các tỉnh khác
            features = [
                'Tỉnh/Thành phố', 'Quận', 'Loại hình nhà ở',
                'Số tầng', 'Số phòng ngủ', 'Diện tích', 'Giấy tờ pháp lý'
            ]

            df_input = self._encode(df, self.map_others)
            y = self.model_others.predict(df_input[features])

        return float(np.expm1(y)[0])


# --- ĐOẠN CODE ĐỂ TEST ---

# 1. Khởi tạo predictor
predictor = HousePricePredictor()

# 2. Dữ liệu test Hà Nội
test_hn = {
    "Tỉnh/Thành phố": "Hà Nội",
    "Quận": "Cầu Giấy",
    "Phường": "Dịch Vọng",
    "Loại hình nhà ở": "Nhà mặt phố",
    "Giấy tờ pháp lý": "Sổ đỏ/ Sổ hồng",
    "Số tầng": 5,
    "Số phòng ngủ": 4,
    "Diện tích": 50
}

# 3. Dữ liệu test tỉnh khác
test_tinh = {
    "Tỉnh/Thành phố": "TP. Hồ Chí Minh",
    "Quận": "Quận 1",
    "Loại hình nhà ở": "Nhà ngõ, hẻm",
    "Giấy tờ pháp lý": "Sổ đỏ/ Sổ hồng",
    "Số tầng": 2,
    "Số phòng ngủ": 2,
    "Diện tích": 40
}

# 4. In kết quả
print(f"Giá dự báo Hà Nội: {predictor.predict(test_hn):.2f} triệu/m2")
print(f"Giá dự báo TP.HCM: {predictor.predict(test_tinh):.2f} triệu/m2")