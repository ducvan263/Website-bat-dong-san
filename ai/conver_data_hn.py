import json
import csv

# ==============================
# CONFIG
# ==============================
INPUT_JSON = "datasets/data_hn.json"     # file json (mỗi dòng 1 object)
OUTPUT_CSV = "data_hn.csv"     # file csv xuất ra


def main():
    rows = []

    # Đọc file JSON lines
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    if not rows:
        print("❌ File JSON rỗng")
        return

    # Lấy header từ keys của object đầu tiên
    fieldnames = list(rows[0].keys())

    # Ghi CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Done! Converted {len(rows)} records → {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
