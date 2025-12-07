import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

DB = "longchau.db"

if os.path.exists(DB):
    os.remove(DB)
    print("Đã xoá DB cũ.")

conn = sqlite3.connect(DB)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_url TEXT PRIMARY KEY,
    product_name TEXT,
    price REAL,
    unit TEXT,
    original_price REAL
)
""")
conn.commit()

driver = webdriver.Chrome()
BASE_URL = "https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang?page="


def clean_price(txt):
    if not txt:
        return None
    txt = txt.replace(".", "").replace("đ", "").strip()
    return int(txt) if txt.isdigit() else None


all_links = []
MAX_PAGES = 3

for page in range(1, MAX_PAGES + 1):
    url = BASE_URL + str(page)
    print("Đang cào:", url)
    driver.get(url)
    time.sleep(2)

    products = driver.find_elements(
        By.CSS_SELECTOR,
        "#category-page_products-section div.h-full.relative"
    )

    print("Tìm thấy:", len(products))

    for p in products:
        try:
            link = p.find_element(By.CSS_SELECTOR, "a.block").get_attribute("href")
            all_links.append(link)
        except:
            pass

all_links = list(set(all_links))
print("Tổng link thu được:", len(all_links))

# ========== Cào chi tiết ==========
for link in all_links[:50]:  # cào 50 sản phẩm đầu
    print("Cào:", link)
    driver.get(link)
    time.sleep(1)

    try:
        name = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
    except:
        name = ""

    # giá
    try:
        price_txt = driver.find_element(By.CSS_SELECTOR, ".text-blue-5").text
        price = clean_price(price_txt)
    except:
        price = None

    # đơn vị
    try:
        unit = driver.find_element(By.CSS_SELECTOR, "p.md\\\\:text-caption2").text
    except:
        unit = None

    # giá gốc (nếu có)
    try:
        orig = driver.find_element(By.CSS_SELECTOR, ".line-through").text
        original_price = clean_price(orig)
    except:
        original_price = None

    cursor.execute("""
        INSERT OR IGNORE INTO products(product_url, product_name, price, unit, original_price)
        VALUES (?, ?, ?, ?, ?)
    """, (link, name, price, unit, original_price))
    conn.commit()

driver.quit()
conn.close()
