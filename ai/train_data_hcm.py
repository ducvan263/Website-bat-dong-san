# ================================
# TRAIN GIÁ ĐẤT / m2 - CHỈ TP.HCM
# - Chỉ giữ dữ liệu TP.HCM từ đầu
# - Bỏ province encoder (không cần)
# - Train + Predict chỉ cho HCM
# ================================

import pandas as pd
import numpy as np
import re
import os
import json
import time
import joblib
from tqdm import tqdm
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from geopy.geocoders import Nominatim

# -------------------------
# 1. LOAD DATA
# -------------------------
DATA_FILE = "datasets/chotot_data.json"
CACHE_FILE = "datasets/location_cache.csv"
MODEL_FILE = "models/hcm/rf_price_m2_hcm.joblib"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# -------------------------
# 2. PARSE FUNCTIONS
# -------------------------
def parse_float(text):
    if pd.isna(text): return 0.0
    text = str(text).replace(',', '.')
    m = re.search(r"\d+(\.\d+)?", text)
    return float(m.group()) if m else 0.0


def parse_price_per_m2(text):
    if pd.isna(text): return np.nan
    text = str(text).lower().replace(' ', '').replace(',', '.')
    value = parse_float(text)
    if 'triệu' in text: return value * 1_000_000
    if 'tỷ' in text: return value * 1_000_000_000
    return value

# -------------------------
# 3. FEATURE ENGINEERING
# -------------------------

df['price_per_m2'] = df['Giá/m2:'].apply(parse_price_per_m2)
df = df[df['price_per_m2'] > 1_000_000].reset_index(drop=True)

# Numeric
df['area_m2'] = df['Diện tích đất:'].apply(parse_float)
df['width'] = df['Chiều ngang:'].apply(parse_float)
df['length'] = df['Chiều dài:'].apply(parse_float)

# ---- CHỈ GIỮ TP.HCM ----
def is_hcm(loc):
    if pd.isna(loc): return False
    return ('Hồ Chí Minh' in loc) or ('TP HCM' in loc) or ('Tp Hồ Chí Minh' in loc)

df = df[df['location'].apply(is_hcm)].reset_index(drop=True)
print(f"Sau khi lọc TP.HCM: {df.shape[0]} mẫu")

# ---- OUTLIER (3.0*IQR) ----
Q1 = df['price_per_m2'].quantile(0.25)
Q3 = df['price_per_m2'].quantile(0.75)
IQR = Q3 - Q1
upper = Q3 + 3.0 * IQR
df = df[df['price_per_m2'] <= upper].reset_index(drop=True)
print(f"Sau khi lọc outlier: {df.shape[0]} mẫu")

# ---- DISTRICT ----
def extract_district(location):
    if pd.isna(location): return 'Unknown'
    m = re.search(r'(Quận|Huyện)\s*\d{1,2}|Thành Phố Thủ Đức', location, re.IGNORECASE)
    if m: return m.group(0).replace('Thành Phố', 'TP').strip()
    names = ['Bình Thạnh','Tân Bình','Gò Vấp','Phú Nhuận','Bình Tân','Tân Phú',
             'Thủ Đức','Củ Chi','Hóc Môn','Bình Chánh','Nhà Bè','Cần Giờ']
    for n in names:
        if n in location: return n
    return 'Other'

df['district'] = df['location'].apply(extract_district)

# Encode
le_land = LabelEncoder()
le_district = LabelEncoder()

df['land_type'] = le_land.fit_transform(df['Loại hình đất:'].fillna('Unknown'))
df['district_code'] = le_district.fit_transform(df['district'])

# -------------------------
# 4. GEOCODING + CACHE
# -------------------------
geolocator = Nominatim(user_agent="hcm_price_ml")


def geocode_safe(addr):
    try:
        loc = geolocator.geocode(addr, timeout=10)
        if loc: return loc.latitude, loc.longitude
    except:
        pass
    return np.nan, np.nan

if os.path.exists(CACHE_FILE):
    cache = pd.read_csv(CACHE_FILE)
    df = df.merge(cache, on='location', how='left')
else:
    lats, lons = [], []
    for addr in tqdm(df['location'], desc='Geocoding'):
        lat, lon = geocode_safe(addr)
        lats.append(lat); lons.append(lon)
        time.sleep(1)
    df['lat'] = lats; df['lon'] = lons
    df[['location','lat','lon']].to_csv(CACHE_FILE, index=False)

# Fill missing
df['lat'] = df['lat'].fillna(df['lat'].mean())
df['lon'] = df['lon'].fillna(df['lon'].mean())

# -------------------------
# 5. DATASET
# -------------------------
FEATURES = ['area_m2','width','length','land_type','district_code','lat','lon']
X = df[FEATURES]
y = np.log1p(df['price_per_m2'])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -------------------------
# 6. TRAIN
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

rf = RandomForestRegressor(
    n_estimators=400,
    max_depth=20,
    min_samples_leaf=3,
    random_state=42,
    n_jobs=-1
)

rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

rmse = np.sqrt(mean_squared_error(np.expm1(y_test), np.expm1(y_pred)))
print(f"RMSE TP.HCM (VNĐ/m²): {rmse:,.0f}")

# -------------------------
# 7. SAVE
# -------------------------
joblib.dump(rf, MODEL_FILE)
joblib.dump(scaler, 'models/hcm/scaler.joblib')
joblib.dump(le_land, 'models/hcm/le_land.joblib')
joblib.dump(le_district, 'models/hcm/le_district.joblib')

print('Saved HCM-only model')

# -------------------------
# 8. PREDICT (HCM ONLY)
# -------------------------

def predict_price(sample: dict):
    if not is_hcm(sample.get('location','')):
        raise ValueError('Model chỉ hỗ trợ TP.HCM')

    area = parse_float(sample.get('Diện tích đất:', 0))
    width = parse_float(sample.get('Chiều ngang:', 0))
    length = parse_float(sample.get('Chiều dài:', 0))

    land = le_land.transform([sample.get('Loại hình đất:','Unknown')])[0]
    district = extract_district(sample.get('location',''))
    try:
        district_code = le_district.transform([district])[0]
    except ValueError:
        district_code = -1

    lat, lon = geocode_safe(sample.get('location',''))
    if np.isnan(lat): lat = df['lat'].mean()
    if np.isnan(lon): lon = df['lon'].mean()

    X_new = scaler.transform([[area,width,length,land,district_code,lat,lon]])
    return np.expm1(rf.predict(X_new)[0])


# -------------------------
# 9. TEST NHANH
# -------------------------
if __name__ == '__main__':
    sample = {
    "Diện tích đất:": "105 m2",
    "Chiều ngang:": "5 m",
    "Chiều dài:": "16 m",
    "Loại hình đất:": "Đất thổ cư",
    "location": "Đường Quốc Hương, Quận 2, TP Hồ Chí Minh"
    }


    pred = predict_price(sample)


    print("===== TEST TP.HCM =====")
    print(f"Giá dự đoán : {pred:,.0f} VNĐ/m²")
