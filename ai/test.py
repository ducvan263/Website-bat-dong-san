import cloudscraper
from bs4 import BeautifulSoup
import time, random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36",
]

scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "desktop": True}
)

# 🔥 Warm-up session
scraper.get("https://batdongsan.com.vn", timeout=10)
time.sleep(3)

BASE_URL = "https://batdongsan.com.vn/nha-dat-ban"
all_posts = []

for page in range(1, 4):
    for attempt in range(3):  # retry
        print(f"📄 Page {page} – attempt {attempt+1}")

        scraper.headers.update({
            "User-Agent": random.choice(USER_AGENTS)
        })

        url = BASE_URL if page == 1 else f"{BASE_URL}/p{page}"
        res = scraper.get(url, timeout=15)

        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select(
            "a.js__product-link-for-product-id, a.re__link-product"
        )

        if items:
            print(f"✅ Tìm thấy {len(items)} tin")
            break
        else:
            print("⚠️ Bị chặn – retry...")
            time.sleep(random.uniform(3, 6))

    for item in items:
        link = item.get("href")
        if not link.startswith("http"):
            link = "https://batdongsan.com.vn" + link

        all_posts.append({
            "title": item.get("title"),
            "link": link
        })

    time.sleep(random.uniform(2, 5))

print("✅ Hoàn tất!")
print(f"📦 Tổng số tin: {len(all_posts)}")
