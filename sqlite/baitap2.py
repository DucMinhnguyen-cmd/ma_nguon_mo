import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re
import os

# ===========================
# 1. SETUP DATABASE
# ===========================

DB_FILE = "painters.db"

if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print("Đã xoá file DB cũ.")

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS painters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    birth TEXT,
    death TEXT,
    nationality TEXT
)
""")
conn.commit()


# ===========================
# 2. LẤY DANH SÁCH LINK HỌA SĨ (CHỮ F)
# ===========================

driver = webdriver.Chrome()
url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22F%22"
driver.get(url)
time.sleep(3)

ul_tags = driver.find_elements(By.TAG_NAME, "ul")
ul_painters = None

# Tìm UL có chứa "Fragonard" → list chính xác
for ul in ul_tags:
    if "Fragonard" in ul.text:
        ul_painters = ul
        break

if ul_painters is None:
    print("Không tìm thấy danh sách họa sĩ.")
    driver.quit()
    exit()

li_tags = ul_painters.find_elements(By.TAG_NAME, "li")
all_links = []

for li in li_tags:
    try:
        link = li.find_element(By.TAG_NAME, "a").get_attribute("href")
        all_links.append(link)
    except:
        continue

print("Tổng số link tìm được:", len(all_links))


# ===========================
# 3. CÀO TỪNG TRANG HỌA SĨ
# ===========================

painters = []

for count, link in enumerate(all_links):
    if count >= 10:    # Giới hạn 10 họa sĩ
        break

    driver.get(link)
    time.sleep(2)

    # ========= NAME =========
    try:
        name = driver.find_element(By.TAG_NAME, "h1").text
    except:
        name = ""

    # ========= BIRTH =========
    try:
        birth_text = driver.find_element(By.XPATH, "//th[contains(text(),'Born')]/following-sibling::td").text
        birth_match = re.findall(r'\d{1,2}\s[A-Za-z]+\s\d{4}', birth_text)
        birth = birth_match[0] if birth_match else birth_text.split("\n")[0]
    except:
        birth = ""

    # ========= DEATH =========
    try:
        death_text = driver.find_element(By.XPATH, "//th[contains(text(),'Died')]/following-sibling::td").text
        death_match = re.findall(r'\d{1,2}\s[A-Za-z]+\s\d{4}', death_text)
        death = death_match[0] if death_match else death_text.split("\n")[0]
    except:
        death = ""

    # ========= NATIONALITY (lấy từ cuối dòng Born) =========
    try:
        parts = birth_text.split(',')
        nationality = parts[-1].strip()
    except:
        nationality = "Unknown"

    painters.append([name, birth, death, nationality])
    print("Đã cào:", name)


driver.quit()


# ===========================
# 4. LƯU VÀO SQLITE
# ===========================

cursor.executemany(
    "INSERT INTO painters (name, birth, death, nationality) VALUES (?, ?, ?, ?)",
    painters
)
conn.commit()


# ===========================
# 5. TRUY VẤN & HIỂN THỊ KẾT QUẢ
# ===========================

print("\n==========================")
print("A. THỐNG KÊ TOÀN CỤC")
print("==========================")

# 1. Tổng số họa sĩ
cursor.execute("SELECT COUNT(*) FROM painters")
print("Tổng số họa sĩ:", cursor.fetchone()[0])

# 2. 5 dòng đầu tiên
print("\n5 dòng dữ liệu đầu tiên:")
cursor.execute("SELECT name, birth, death, nationality FROM painters LIMIT 5")
for row in cursor.fetchall():
    print(row)

# 3. Quốc tịch duy nhất
print("\nDanh sách quốc tịch:")
cursor.execute("SELECT DISTINCT nationality FROM painters")
for row in cursor.fetchall():
    print("-", row[0])

print("\n==========================")
print("B. LỌC VÀ TÌM KIẾM")
print("==========================")

# 4. Tên bắt đầu bằng F
print("\nHọa sĩ tên bắt đầu bằng F:")
cursor.execute("SELECT name FROM painters WHERE name LIKE 'F%'")
for r in cursor.fetchall():
    print("-", r[0])

# 5. Quốc tịch French
print("\nHọa sĩ quốc tịch French:")
cursor.execute("SELECT name, nationality FROM painters WHERE nationality LIKE '%France%' OR nationality LIKE '%French%'")
for r in cursor.fetchall():
    print("-", r)

# 6. Không có quốc tịch
print("\nHọa sĩ không có quốc tịch:")
cursor.execute("SELECT name FROM painters WHERE nationality='' OR nationality IS NULL")
for r in cursor.fetchall():
    print("-", r[0])

# 7. Có cả birth + death
print("\nHọa sĩ có cả ngày sinh và mất:")
cursor.execute("""
SELECT name, birth, death 
FROM painters
WHERE birth != '' AND death != ''
""")
for r in cursor.fetchall():
    print("-", r[0], "| Born:", r[1], "| Died:", r[2])

# 8. Tên chứa Fales
print("\nHọa sĩ có tên chứa 'Fales':")
cursor.execute("SELECT name FROM painters WHERE name LIKE '%Fales%'")
for r in cursor.fetchall():
    print("-", r[0])


print("\n==========================")
print("C. NHÓM VÀ SẮP XẾP")
print("==========================")

# 9. Sắp xếp A-Z
print("\nTên họa sĩ sắp xếp A-Z:")
cursor.execute("SELECT name FROM painters ORDER BY name ASC")
for r in cursor.fetchall():
    print("-", r[0])

# 10. Nhóm theo quốc tịch
print("\nThống kê theo quốc tịch:")
cursor.execute("""
SELECT nationality, COUNT(*) 
FROM painters
GROUP BY nationality
ORDER BY COUNT(*) DESC
""")
for r in cursor.fetchall():
    print(f"- {r[0]}: {r[1]} họa sĩ")

conn.close()
