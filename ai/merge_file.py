import pandas as pd

# Đọc từng file
df1 = pd.read_csv("data_hn.csv", encoding="utf-8-sig")
df2 = pd.read_csv("dataset_chotot_cleaned.csv", encoding="utf-8-sig")
df3 = pd.read_csv("real_estate_standardized.csv", encoding="utf-8-sig")

# Gộp dataset
df_all = pd.concat([df1, df2, df3], axis=0, ignore_index=True)

# Xuất ra file mới
df_all.to_csv("dataset_bds_full.csv", index=False, encoding="utf-8-sig")

print("✅ Đã gộp xong:", df_all.shape)
