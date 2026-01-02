from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd


def scrape_batdongsan_pages(num_pages=3):
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    data = []

    for page in range(1, num_pages + 1):
        url = f"https://batdongsan.com.vn/nha-dat-ban/p{page}"
        driver.get(url)
        time.sleep(20)  # đợi load trang

        listings = driver.find_elements(By.CLASS_NAME, "re__card-info")

        for item in listings:
            try:
                title = item.find_element(By.CLASS_NAME, "re__card-title").text
                price = item.find_element(By.CLASS_NAME, "re__card-config-price").text
                area = item.find_element(By.CLASS_NAME, "re__card-config-area").text
                location = item.find_element(By.CLASS_NAME, "re__card-location").text

                data.append({
                    "Tiêu đề": title,
                    "Giá": price,
                    "Diện tích": area,
                    "Địa điểm": location
                })
            except:
                continue

    driver.quit()
    df = pd.DataFrame(data)
    df.to_csv("batdongsan_data.csv", index=False, encoding='utf-8-sig')
    print(f"Đã lấy được {len(data)} tin đăng từ {num_pages} trang")


scrape_batdongsan_pages(3)