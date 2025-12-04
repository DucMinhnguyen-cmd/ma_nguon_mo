import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import re
import os # Thêm thư viện để kiểm tra/xóa file DB (tùy chọn)

######################################################
## I. Cấu hình và Chuẩn bị
######################################################

# Thiết lập tên file DB và Bảng
DB_FILE = 'Painters_Data.db'
TABLE_NAME = 'painters_info'
all_links = []

# Tùy chọn cho Chrome (có thể chạy ẩn nếu cần, nhưng để dễ debug thì không dùng)
# chrome_options = Options()
# chrome_options.add_argument("--headless") 

# Nếu muốn bắt đầu với DB trống, có thể xóa file cũ (Tùy chọn)
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"Đã xóa file DB cũ: {DB_FILE}")

# Mở kết nối SQLite và tạo bảng nếu chưa tồn tại
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Tạo bảng
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    name TEXT PRIMARY KEY, -- Sử dụng tên làm khóa chính để tránh trùng lặp
    birth TEXT,
    death TEXT,
    nationality TEXT
);
"""
cursor.execute(create_table_sql)
conn.commit()
print(f"Đã kết nối và chuẩn bị bảng '{TABLE_NAME}' trong '{DB_FILE}'.")

# Hàm đóng driver an toàn
def safe_quit_driver(driver):
    try:
        if driver:
            driver.quit()
    except:
        pass

######################################################
## II. Lấy Đường dẫn (URLs)
######################################################

print("\n--- Bắt đầu Lấy Đường dẫn ---")

# Lặp qua ký tự 'F' (chr(70))
for i in range(70, 71): 
    driver = None
    try:
        driver = webdriver.Chrome() # Khởi tạo driver cho phần này
        url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22"+chr(i)+"%22"
        driver.get(url)
        time.sleep(3)

        # Lấy tất cả thẻ ul
        ul_tags = driver.find_elements(By.TAG_NAME, "ul")
        
        # Thử chọn chỉ mục (index) 20. Cần kiểm tra lại nếu index này thay đổi.
        if len(ul_tags) > 20:
            ul_painters = ul_tags[20] 
            li_tags = ul_painters.find_elements(By.TAG_NAME, "li")

            # Lọc các đường dẫn hợp lệ (có thuộc tính href)
            links = [tag.find_element(By.TAG_NAME, "a").get_attribute("href") 
                     for tag in li_tags if tag.find_elements(By.TAG_NAME, "a")]
            all_links.extend(links)
        else:
            print(f"Lỗi: Không tìm thấy thẻ ul ở chỉ mục 20 cho ký tự {chr(i)}.")

    except Exception as e:
        print(f"Lỗi khi lấy links cho ký tự {chr(i)}: {e}")
    finally:
        safe_quit_driver(driver) # Đóng driver sau khi xong phần này

print(f"Hoàn tất lấy đường dẫn. Tổng cộng {len(all_links)} links đã tìm thấy.")

######################################################
## III. Lấy thông tin & LƯU TRỮ TỨC THỜI
######################################################

print("\n--- Bắt đầu Cào và Lưu Trữ Tức thời ---")
count = 0
for link in all_links:
    # Giới hạn số lượng truy cập để thử nghiệm nhanh
    if (count >= 5): # Đã tăng lên 5 họa sĩ để có thêm dữ liệu mẫu
        break
    count = count + 1

    driver = None
    try:
        driver = webdriver.Chrome() 
        driver.get(link)
        time.sleep(2)

        # 1. Lấy tên họa sĩ
        try:
            name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            name = ""
        
        # 2. Lấy ngày sinh (Born)
        try:
            birth_element = driver.find_element(By.XPATH, "//th[text()='Born']/following-sibling::td")
            birth = birth_element.text
            # Trích xuất định dạng ngày (ví dụ: 12 June 1900)
            birth_match = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', birth)
            birth = birth_match[0] if birth_match else ""
        except:
            birth = ""
            
        # 3. Lấy ngày mất (Died)
        try:
            death_element = driver.find_element(By.XPATH, "//th[text()='Died']/following-sibling::td")
            death = death_element.text
            death_match = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', death)
            death = death_match[0] if death_match else ""
        except:
            death = ""
            
        # 4. Lấy quốc tịch (Nationality)
        try:
            nationality_element = driver.find_element(By.XPATH, "//th[text()='Nationality']/following-sibling::td")
            # Cần lấy text và chỉ lấy phần tử đầu tiên nếu có nhiều quốc tịch
            nationality = nationality_element.text.split('\n')[0]
        except:
            nationality = ""

        safe_quit_driver(driver)
        
        # 5. LƯU TỨC THỜI VÀO SQLITE
        insert_sql = f"""
        INSERT OR IGNORE INTO {TABLE_NAME} (name, birth, death, nationality) 
        VALUES (?, ?, ?, ?);
        """
        # Sử dụng 'INSERT OR IGNORE' để bỏ qua nếu Tên (PRIMARY KEY) đã tồn tại
        cursor.execute(insert_sql, (name, birth, death, nationality))
        conn.commit()
        print(f"  --> Đã lưu thành công: {name}")

    except Exception as e:
        print(f"Lỗi khi xử lý hoặc lưu họa sĩ {link}: {e}")
        safe_quit_driver(driver)
        
print("\nHoàn tất quá trình cào và lưu dữ liệu tức thời.")

# 1. Đếm tổng số họa sĩ
cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
total_painters = cursor.fetchone()[0]
print(f"1. Tổng số họa sĩ: {total_painters}")

# 2. Hiển thị 5 dòng đầu tiên
print("\n2. 5 dòng dữ liệu đầu tiên:")
cursor.execute(f"SELECT * FROM {TABLE_NAME} LIMIT 5")
rows = cursor.fetchall()
for r in rows:
    print(r)

# 3. Liệt kê danh sách quốc tịch duy nhất
print("\n3. Các quốc tịch duy nhất:")
cursor.execute(f"""
SELECT DISTINCT nationality 
FROM {TABLE_NAME}
WHERE nationality IS NOT NULL AND nationality != ''
""")
unique_nationalities = cursor.fetchall()
for nat in unique_nationalities:
    print(nat[0])

print("\n================ B. LỌC VÀ TÌM KIẾM ================")

# 4. Họa sĩ có tên bắt đầu bằng F
print("\n4. Họa sĩ có tên bắt đầu bằng 'F':")
cursor.execute(f"SELECT name FROM {TABLE_NAME} WHERE name LIKE 'F%'")
for r in cursor.fetchall():
    print(r[0])

# 5. Quốc tịch chứa 'French'
print("\n5. Họa sĩ có quốc tịch chứa 'French':")
cursor.execute(f"""
SELECT name, nationality
FROM {TABLE_NAME}
WHERE nationality LIKE '%French%'
""")
for r in cursor.fetchall():
    print(r)

# 6. Họa sĩ không có quốc tịch
print("\n6. Họa sĩ không có thông tin quốc tịch:")
cursor.execute(f"""
SELECT name 
FROM {TABLE_NAME}
WHERE nationality IS NULL 
   OR nationality = ''
""")
for r in cursor.fetchall():
    print(r[0])

# 7. Có cả ngày sinh và ngày mất
print("\n7. Họa sĩ có cả ngày sinh và ngày mất:")
cursor.execute(f"""
SELECT name
FROM {TABLE_NAME}
WHERE birth != '' AND birth IS NOT NULL
  AND death != '' AND death IS NOT NULL
""")
for r in cursor.fetchall():
    print(r[0])

# 8. Tên chứa 'Fales'
print("\n8. Thông tin họa sĩ có tên chứa 'Fales':")
cursor.execute(f"""
SELECT *
FROM {TABLE_NAME}
WHERE name LIKE '%Fales%'
""")
results = cursor.fetchall()
for row in results:
    print(row)

print("\n================ C. NHÓM VÀ SẮP XẾP ================")

# 9. Sắp xếp theo tên A-Z
print("\n9. Danh sách họa sĩ sắp xếp A-Z:")
cursor.execute(f"SELECT name FROM {TABLE_NAME} ORDER BY name ASC")
for r in cursor.fetchall():
    print(r[0])

# 10. Đếm số lượng họa sĩ theo từng quốc tịch
print("\n10. Số lượng họa sĩ theo từng quốc tịch:")
cursor.execute(f"""
SELECT nationality, COUNT(*)
FROM {TABLE_NAME}
WHERE nationality IS NOT NULL AND nationality != ''
GROUP BY nationality
ORDER BY COUNT(*) DESC
""")
for r in cursor.fetchall():
    print(f"{r[0]} : {r[1]}")

