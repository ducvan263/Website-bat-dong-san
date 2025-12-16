import joblib
import pandas as pd

model = joblib.load("ai/price_model.pkl")

sample = {
    "area": 9000,
    "width": 40,
    "length": 178,
    "land_type": "Đất nông nghiệp",
    "legal": "Đã có sổ"
}

df = pd.DataFrame([sample])
price = model.predict(df)[0]

print("Giá dự đoán:", f"{int(price):,} VNĐ")
