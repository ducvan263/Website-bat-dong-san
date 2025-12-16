import json
import re
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error


# ========= HÀM XỬ LÝ =========
def parse_price(price_str):
    if not price_str:
        return None
    price_str = price_str.lower().replace(',', '.')
    if 'tỷ' in price_str:
        return float(re.findall(r'[\d\.]+', price_str)[0]) * 1e9
    if 'triệu' in price_str:
        return float(re.findall(r'[\d\.]+', price_str)[0]) * 1e6
    return None


def parse_number(text):
    if not text:
        return None
    return float(re.findall(r'[\d\.]+', text.replace('.', ''))[0])


# ========= LOAD DATA =========
with open('ai/datasets/chotot_data.json', encoding='utf-8') as f:
    raw_data = json.load(f)

rows = []
for item in raw_data:
    rows.append({
        "price": parse_price(item.get("price")),
        "area": parse_number(item.get("Diện tích đất:")),
        "width": parse_number(item.get("Chiều ngang:")),
        "length": parse_number(item.get("Chiều dài:")),
        "land_type": item.get("Loại hình đất:"),
        "legal": item.get("Giấy tờ pháp lý:")
    })

df = pd.DataFrame(rows).dropna()

print("Số dòng hợp lệ:", len(df))

# ========= TRAIN =========
X = df[["area", "width", "length", "land_type", "legal"]]
y = df["price"]

cat_cols = ["land_type", "legal"]
num_cols = ["area", "width", "length"]

preprocess = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ("num", "passthrough", num_cols)
])

model = Pipeline([
    ("prep", preprocess),
    ("rf", RandomForestRegressor(
        n_estimators=200,
        random_state=42
    ))
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

print("MAE:", int(mae))

joblib.dump(model, "ai/price_model.pkl")
print("✅ Đã lưu model ai/price_model.pkl")
