import cloudscraper
from bs4 import BeautifulSoup
import os
import json
import time
import random

# ================= CONFIG =================
BASE_URL = "https://batdongsan.com.vn/ban-nha-rieng"
SAVE_DIR = "data"
IMG_DIR = os.path.join(SAVE_DIR, "property_images")
os.makedirs(IMG_DIR, exist_ok=True)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36",
]

scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "desktop": True}
)


# ================= FUNCTIONS =================
def get_text(soup, selector):
    el = soup.select_one(selector)
    return el.get_text(strip=True) if el else None


def crawl_property(link, idx, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            scraper.headers.update({"User-Agent": random.choice(USER_AGENTS)})
            res = scraper.get(link, timeout=20)

            if res.status_code != 200:
                print(f"      ⚠️ Thử lại {attempt}/{max_retries} do Status {res.status_code}")
                time.sleep(random.uniform(5, 10))
                continue

            soup = BeautifulSoup(res.text, "html.parser")

            # Kiểm tra xem có lấy được dữ liệu cốt lõi không (ví dụ tiêu đề)
            title = get_text(soup, "h1.re__pr-title")
            img_tags = soup.select(".re__media-thumb-item img")

            # Nếu không thấy tiêu đề hoặc không thấy ảnh, có thể bị chặn/load lỗi
            if not title or not img_tags:
                print(f"      ⚠️ Thử lại {attempt}/{max_retries} do không tìm thấy dữ liệu (Title/Images)")
                time.sleep(random.uniform(5, 10))
                continue

            # --- BẮT ĐẦU TRÍCH XUẤT NẾU DỮ LIỆU OK ---
            short_address = get_text(soup, "span.re__pr-short-description")
            desc_div = soup.select_one("div.re__detail-content")
            description = desc_div.get_text(separator="\n", strip=True) if desc_div else None

            contact_span = soup.select_one("span.js__btn-tracking")
            contact_name = contact_span.get("data-kyc-name") if contact_span else None
            contact_phone = contact_span.get_text(strip=True) if contact_span else None

            specs = {item.select_one(".re__pr-specs-content-item-title").text.strip():
                         item.select_one(".re__pr-specs-content-item-value").text.strip()
                     for item in soup.select(".re__pr-specs-content-item") if
                     item.select_one(".re__pr-specs-content-item-title")}

            config = {item.select_one(".title").text.strip(): item.select_one(".value").text.strip()
                      for item in soup.select(".re__pr-config-item") if item.select_one(".title")}

            # Xử lý ảnh
            imgs = []
            img_folder = os.path.join(IMG_DIR, str(idx))
            os.makedirs(img_folder, exist_ok=True)
            downloaded_urls = set()

            for i, img in enumerate(img_tags):
                src = img.get("data-src") or img.get("src")
                if src and src.startswith("http") and src not in downloaded_urls:
                    downloaded_urls.add(src)
                    try:
                        img_res = scraper.get(src, timeout=10)
                        if img_res.status_code == 200:
                            img_path = os.path.join(img_folder, f"img_{len(downloaded_urls)}.jpg")
                            with open(img_path, "wb") as f:
                                f.write(img_res.content)
                            imgs.append(img_path)
                    except:
                        pass

            return {
                "id": idx, "title": title, "short_address": short_address,
                "description": description, "contact_name": contact_name,
                "contact_phone": contact_phone, "specs": specs,
                "config": config, "images": imgs, "url": link
            }

        except Exception as e:
            print(f"      ❌ Lỗi kết nối ở lần thử {attempt}: {e}")
            time.sleep(random.uniform(5, 10))

    return None  # Trả về None nếu sau 3 lần vẫn thất bại


# ================= MAIN EXECUTION =================

# (Bước 1: Lấy link tin đăng - giữ nguyên như cũ hoặc áp dụng retry tương tự)
post_links = []
MAX_PAGES = 25

for page in range(1, MAX_PAGES + 1):
    url = BASE_URL if page == 1 else f"{BASE_URL}/p{page}"
    print(f"🔍 Quét trang {page}...")
    try:
        res = scraper.get(url, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("a.js__product-link-for-product-id")
        for item in items:
            link = item.get("href")
            if link:
                full_link = "https://batdongsan.com.vn" + link if not link.startswith("http") else link
                if full_link not in post_links: post_links.append(full_link)
    except:
        pass
    time.sleep(3)

# Bước 2: Crawl chi tiết với Retry
all_data = []
for idx, link in enumerate(post_links, 1):
    print(f"🏠 [{idx}/{len(post_links)}] Đang xử lý: {link}")
    data = crawl_property(link, idx)
    if data:
        all_data.append(data)
    else:
        print(f"      🚫 Bỏ qua tin này sau nhiều lần thử thất bại.")

    time.sleep(random.uniform(3, 5))

# Lưu file
with open(os.path.join(SAVE_DIR, "properties.json"), "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Xong! Thu thập được {len(all_data)} tin.")