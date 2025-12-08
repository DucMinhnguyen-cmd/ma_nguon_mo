# -------------------------------
# BÀI THỰC HÀNH: CÀO DỮ LIỆU LONG CHÂU VÀ LƯU TRỮ SQLITE
# -------------------------------

# Import các thư viện cần thiết
import sqlite3, os, re, time          # sqlite3: làm việc với DB, os: thao tác file, re: regex, time: delay
import pandas as pd                   # pandas: quản lý dữ liệu dạng bảng
from selenium import webdriver        # webdriver: điều khiển trình duyệt
from selenium.webdriver.common.by import By   # By: cách tìm phần tử trên trang
from selenium.webdriver.common.keys import Keys # Keys: gửi phím (PAGE_DOWN...)

# -------------------------------
# 1. TẠO CƠ SỞ DỮ LIỆU SQLITE
# -------------------------------

# Đường dẫn tới file SQLite database
DB_FILE = r"D:\Program\lo\ma_nguon_mo\sqlite\longchau.db"

# Nếu file DB đã tồn tại thì xóa đi để tạo mới
if os.path.exists(DB_FILE): 
    os.remove(DB_FILE)

# Kết nối tới SQLite (nếu chưa có file thì sẽ tự tạo)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Tạo bảng products để lưu thông tin sản phẩm
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_url TEXT PRIMARY KEY,   -- URL sản phẩm, định danh duy nhất
    product_name TEXT,              -- Tên sản phẩm
    unit TEXT,                      -- Đơn vị tính (Hộp, Chai, Vỉ, Viên...)
    price INTEGER,                  -- Giá bán hiện tại (VNĐ)
    original_price INTEGER,         -- Giá gốc/niêm yết (VNĐ)
    img_url TEXT,                   -- Link ảnh sản phẩm
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP -- Thời gian lưu
);
""")
conn.commit()   # Xác nhận tạo bảng

# -------------------------------
# 2. HÀM TIỆN ÍCH
# -------------------------------

def parse_price(text):
    """Chuyển chuỗi giá (vd: '125.000đ') thành số nguyên (125000)."""
    # Loại bỏ tất cả ký tự không phải số bằng regex
    return int(re.sub(r"[^\d]", "", text or "") or 0)

def normalize_unit(name):
    """Xác định đơn vị tính từ tên sản phẩm."""
    n = (name or "").lower()   # Chuyển tên sản phẩm về chữ thường
    # Dùng dict để map từ khóa -> đơn vị
    for k,v in {
        "hộp":"Hộp","chai":"Chai","lọ":"Chai","vỉ":"Vỉ",
        "tuýp":"Tuýp","gói":"Gói","sachet":"Gói",
        "viên":"Viên","capsule":"Viên","tablet":"Viên"
    }.items():
        if k in n: return v    # Nếu tìm thấy từ khóa thì trả về đơn vị
    return "Không rõ"          # Nếu không tìm thấy thì trả về "Không rõ"

# -------------------------------
# 3. CÀO DỮ LIỆU
# -------------------------------

try:
    # Khởi tạo Firefox WebDriver
    driver = webdriver.Firefox()
    # Truy cập vào danh mục sản phẩm Vitamin & Khoáng chất
    driver.get("https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/vitamin-khoang-chat")
    time.sleep(2)  # Chờ trang load

    # Nhấn nút "Xem thêm" nhiều lần để load thêm sản phẩm
    for _ in range(12):   # Lặp tối đa 12 lần
        try:
            # Tìm nút "Xem thêm"
            btns = driver.find_elements(By.XPATH, "//button[contains(., 'Xem thêm')]")
            if not btns: break   # Nếu không có nút thì thoát
            # Click nút bằng JavaScript
            driver.execute_script("arguments[0].click();", btns[0])
            time.sleep(2)   # Chờ load thêm sản phẩm
        except: 
            break   # Nếu lỗi thì thoát vòng lặp

    # Scroll xuống để load ảnh lazy-loading
    body = driver.find_element(By.TAG_NAME, "body")
    [body.send_keys(Keys.PAGE_DOWN) or time.sleep(0.3) for _ in range(10)]

    # Lấy danh sách thẻ sản phẩm (mỗi card là một sản phẩm)
    cards = driver.find_elements(By.XPATH,
        "//div[contains(@class,'rounded-xl') and contains(@class,'bg-white') and contains(@class,'flex-col')]"
    )

    saved = 0  # Biến đếm số sản phẩm đã lưu

    # Vòng lặp qua từng sản phẩm
    for c in cards:
        try:
            # Tên sản phẩm
            name = c.find_element(By.TAG_NAME, "h3").text.strip()
            # Link sản phẩm
            link = c.find_element(By.TAG_NAME, "a").get_attribute("href")
            # Giá bán hiện tại
            price = parse_price(next((e.text for e in c.find_elements(By.CLASS_NAME,"text-blue-5")), ""))
            # Giá gốc (nếu có)
            original_price = parse_price(next((e.text for e in c.find_elements(By.CLASS_NAME,"line-through")), ""))
            # Ảnh sản phẩm
            img = c.find_element(By.TAG_NAME, "img").get_attribute("src")
            # Đơn vị tính
            unit = normalize_unit(name)

            # Lưu vào DB (INSERT OR IGNORE để tránh trùng lặp)
            cursor.execute("INSERT OR IGNORE INTO products VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)",
                            (link,name,unit,price,original_price,img))
            conn.commit()   # Lưu ngay lập tức
            saved += 1
            print(f"Đã lưu: {name[:40]}...")  # In ra tên sản phẩm (40 ký tự đầu)
        except Exception as e:
            print("Lỗi:", e)   # Nếu có lỗi thì in ra

    print(f"✅ Tổng cộng đã lưu {saved} sản phẩm.")
    
finally:

    # Đóng driver và kết nối DB
    driver.quit()  
# Hàm tiện ích: chạy query SQL và trả về kết quả dưới dạng DataFrame (dễ đọc hơn)
def run_query(sql):
    return pd.read_sql_query(sql, conn)

# -------------------------------
# Nhóm 1: Kiểm tra chất lượng dữ liệu
# -------------------------------
print("\n========== Nhóm 1: Kiểm tra chất lượng dữ liệu ==========")

# 1. Kiểm tra trùng lặp theo product_url
print("\n1. Trùng lặp theo product_url:")
print(run_query("""
SELECT product_url, COUNT(*) AS cnt
FROM products
GROUP BY product_url
HAVING cnt > 1;
"""))

# 2. Kiểm tra trùng lặp theo product_name
print("\n2. Trùng lặp theo product_name:")
print(run_query("""
SELECT product_name, COUNT(*) AS cnt
FROM products
GROUP BY product_name
HAVING cnt > 1;
"""))

# 3. Đếm số sản phẩm thiếu giá (price NULL hoặc = 0)
print("\n3. Sản phẩm thiếu giá:")
print(run_query("""
SELECT COUNT(*) AS missing_price
FROM products
WHERE price IS NULL OR price = 0;
"""))

# 4. Kiểm tra logic bất thường: giá bán > giá gốc
print("\n4. Giá bán > Giá gốc:")
print(run_query("""
SELECT product_name, price, original_price
FROM products
WHERE price > original_price AND original_price > 0;
"""))

# 5. Liệt kê các đơn vị tính duy nhất
print("\n5. Các đơn vị tính duy nhất:")
print(run_query("SELECT DISTINCT unit FROM products;"))

# 6. Tổng số sản phẩm đã cào
print("\n6. Tổng số sản phẩm:")
print(run_query("SELECT COUNT(*) AS total_products FROM products;"))


# Nhóm 2: Khảo sát và phân tích
print("\n========== Nhóm 2: Khảo sát và phân tích ==========")

# 7. Top 10 sản phẩm giảm giá nhiều nhất (chênh lệch giữa original_price và price)
print("\n7. Top 10 sản phẩm giảm giá nhiều nhất:")
print(run_query("""
SELECT product_name, original_price, price,
       (original_price - price) AS discount_amount
FROM products
WHERE original_price > price
ORDER BY discount_amount DESC
LIMIT 10;
"""))

# 8. Sản phẩm đắt nhất
print("\n8. Sản phẩm đắt nhất:")
print(run_query("""
SELECT product_name, price
FROM products
ORDER BY price DESC
LIMIT 1;
"""))

# 9. Thống kê số lượng sản phẩm theo đơn vị tính
print("\n9. Thống kê theo đơn vị tính:")
print(run_query("""
SELECT unit, COUNT(*) AS count_unit
FROM products
GROUP BY unit;
"""))

# 10. Tìm sản phẩm có tên chứa "Vitamin C"
print("\n10. Sản phẩm chứa 'Vitamin C':")
print(run_query("SELECT * FROM products WHERE product_name LIKE '%Vitamin C%';"))

# 11. Lọc sản phẩm có giá từ 100k đến 200k
print("\n11. Sản phẩm giá từ 100k đến 200k:")
print(run_query("""
SELECT product_name, price
FROM products
WHERE price BETWEEN 100000 AND 200000;
"""))


# Nhóm 3: Truy vấn nâng cao

print("\n========== Nhóm 3: Truy vấn nâng cao ==========")

# 12. Sắp xếp sản phẩm theo giá bán tăng dần
print("\n12. Sắp xếp theo giá bán tăng dần:")
print(run_query("SELECT product_name, price FROM products ORDER BY price ASC;"))



# Đóng kết nối sau khi chạy xong
conn.close()