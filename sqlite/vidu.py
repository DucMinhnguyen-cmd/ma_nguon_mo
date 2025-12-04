import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import re
import os

######################################################
## I. Cấu hình và Chuẩn bị
######################################################

DB_FILE = 'Painters_Data.db'
TABLE_NAME = 'painters_info'
all_links = []

# Xóa DB cũ (để làm sạch – tùy chọn)
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"Đã xóa file DB cũ: {DB_FILE}")

# Kết nối SQLite
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Tạo bảng
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    name TEXT PRIMARY KEY,
    birth TEXT,
    death TEXT,
    nationality TEXT
);
"""
cursor.execute(create_table_sql)
conn.commit()
print(f"Đã kết nối và chuẩn bị bảng '{TABLE_NAME}' trong '{DB_FILE}'.")

# Đóng driver an toàn
def safe_quit_driver(driver):
    try:
        if driver:
            driver.quit()
    except:
        pass


######################################################
## II. Lấy danh sách link từ Wikipedia
######################################################

print("\n--- Bắt đầu Lấy Đường dẫn ---")

driver = webdriver.Chrome()
url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22F%22"
driver.get(url)
time.sleep(3)

# Lấy tất cả link họa sĩ
links = driver.find_elements(By.CSS_SELECTOR, "div.div-col li a")

all_links = [a.get_attribute("href") for a in links]

driver.quit()

print(f"Đã tìm được {len(all_links)} links họa sĩ.")



######################################################
## III. Cào thông tin và Lưu vào DB
######################################################

print("\n--- Bắt đầu Cào và Lưu ---")

count = 0
for link in all_links:
    if count >= 5:  # Lấy 5 họa sĩ để demo
        break
    count += 1

    driver = None
    try:
        driver = webdriver.Chrome()
        driver.get(link)
        time.sleep(2)

        # Tên
        try:
            name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            name = ""

        # Ngày sinh
        try:
            birth_text = driver.find_element(By.XPATH, "//th[text()='Born']/following-sibling::td").text
            birth_match = re.findall(r"[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}", birth_text)
            birth = birth_match[0] if birth_match else ""
        except:
            birth = ""

        # Ngày mất
        try:
            death_text = driver.find_element(By.XPATH, "//th[text()='Died']/following-sibling::td").text
            death_match = re.findall(r"[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}", death_text)
            death = death_match[0] if death_match else ""
        except:
            death = ""

        # Quốc tịch
        try:
            nationality_element = driver.find_element(By.XPATH, "//th[text()='Nationality']/following-sibling::td")
            nationality = nationality_element.text.split("\n")[0]
        except:
            nationality = ""

        safe_quit_driver(driver)

        # Lưu vào DB
        insert_sql = f"""
        INSERT OR IGNORE INTO {TABLE_NAME} (name, birth, death, nationality)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(insert_sql, (name, birth, death, nationality))
        conn.commit()

        print(f" --> Đã lưu: {name}")

    except Exception as e:
        print(f"Lỗi khi cào dữ liệu từ {link}: {e}")
        safe_quit_driver(driver)

print("\nHoàn tất cào và lưu dữ liệu!")


######################################################
## IV. Thực hiện 10 yêu cầu A – B – C
######################################################

print("\n================ A. THỐNG KÊ VÀ TOÀN CỤC ================")

# 1. Tổng số họa sĩ
cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
print("1. Tổng số họa sĩ:", cursor.fetchone()[0])

# 2. 5 dòng đầu tiên
print("\n2. 5 dòng đầu tiên:")
cursor.execute(f"SELECT * FROM {TABLE_NAME} LIMIT 5")
for row in cursor.fetchall():
    print(row)

# 3. Quốc tịch duy nhất
print("\n3. Quốc tịch duy nhất:")
cursor.execute(f"""
SELECT DISTINCT nationality
FROM {TABLE_NAME}
WHERE nationality IS NOT NULL AND nationality != ''
""")
for nat in cursor.fetchall():
    print(nat[0])


print("\n================ B. LỌC VÀ TÌM KIẾM ================")

# 4. Tên bắt đầu bằng F
print("\n4. Họa sĩ bắt đầu bằng F:")
cursor.execute(f"SELECT name FROM {TABLE_NAME} WHERE name LIKE 'F%'")
for r in cursor.fetchall():
    print(r[0])

# 5. Quốc tịch chứa 'French'
print("\n5. Quốc tịch chứa French:")
cursor.execute(f"""
SELECT name, nationality
FROM {TABLE_NAME}
WHERE nationality LIKE '%French%'
""")
for r in cursor.fetchall():
    print(r)

# 6. Không có quốc tịch
print("\n6. Không có quốc tịch:")
cursor.execute(f"""
SELECT name
FROM {TABLE_NAME}
WHERE nationality = '' OR nationality IS NULL
""")
for r in cursor.fetchall():
    print(r[0])

# 7. Có cả birth & death
print("\n7. Có birth và death:")
cursor.execute(f"""
SELECT name
FROM {TABLE_NAME}
WHERE birth != '' AND death != ''
""")
for r in cursor.fetchall():
    print(r[0])

# 8. Tên chứa Fales
print("\n8. Tên chứa 'Fales':")
cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE name LIKE '%Fales%'")
for r in cursor.fetchall():
    print(r)


print("\n================ C. NHÓM VÀ SẮP XẾP ================")

# 9. Sắp xếp A-Z
print("\n9. Danh sách theo tên A-Z:")
cursor.execute(f"SELECT name FROM {TABLE_NAME} ORDER BY name ASC")
for r in cursor.fetchall():
    print(r[0])

# 10. Nhóm theo quốc tịch
print("\n10. Đếm họa sĩ theo quốc tịch:")
cursor.execute(f"""
SELECT nationality, COUNT(*)
FROM {TABLE_NAME}
WHERE nationality != ''
GROUP BY nationality
ORDER BY COUNT(*) DESC
""")
for r in cursor.fetchall():
    print(f"{r[0]} : {r[1]}")

# Đóng kết nối
conn.close()
print("\nĐã đóng kết nối DB. Hoàn tất tất cả các bước.")