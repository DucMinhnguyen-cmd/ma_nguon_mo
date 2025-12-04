from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import pandas as pd # Cần import lại pandas
import time

# Bỏ qua import Service, Options thủ công nếu không cần cấu hình headless

# -------------------------------
# 1. Khởi tạo Firefox (Sử dụng cách đơn giản nhất để Selenium tự động quản lý Driver)
# -------------------------------
# Đảm bảo bạn đã CẬP NHẬT Selenium mới nhất và đã cài đặt Firefox.
driver = webdriver.Firefox() 
wait = WebDriverWait(driver, 15) # Thiết lập chờ tối đa 15 giây

# -------------------------------
# 2. Mở trang GOCHEK
# -------------------------------
url = "https://gochek.vn/"
driver.get(url)
print(f"Truy cập trang: {url}")
time.sleep(2) 

# ----------------------------
# 3. Click "Xem thêm" để load toàn bộ sản phẩm
# ----------------------------
print("Đang click nút 'Xem thêm' để tải thêm sản phẩm...")
while True:
    try:
        view_more_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Xem thêm')]"))
        )
        
        driver.execute_script("arguments[0].scrollIntoView(true);", view_more_button)
        time.sleep(0.5) 
        
        view_more_button.click()
        time.sleep(2) 
        
    except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
        print("Đã tải hết sản phẩm hoặc không tìm thấy nút 'Xem thêm' nữa.")
        break
    except Exception as e:
        print(f"Lỗi không xác định khi click 'Xem thêm': {e}")
        break


# ----------------------------
# 4. Cuộn trang để load sản phẩm lazy-load
# ----------------------------
print("Đang cuộn trang để tải các sản phẩm lazy-load (nếu có)...")
last_height = driver.execute_script("return document.body.scrollHeight")
for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
time.sleep(2)


# ----------------------------
# 5. Thu thập thông tin sản phẩm
# ----------------------------
stt, ten_san_pham, gia_goc, gia_km, gia_ban, hinh_anh = [], [], [], [], [], []
products = driver.find_elements(By.CSS_SELECTOR, "div.product-item") 
print(f"Tìm thấy tổng cộng {len(products)} sản phẩm để cào.")

for i, sp in enumerate(products, 1):
    try:
        name_element = sp.find_element(By.CSS_SELECTOR, 'h3.product-title')
        name = name_element.text.strip()
    except: name = ''

    try:
        original_price = sp.find_element(By.CLASS_NAME, 'original-price').text.strip()
    except: original_price = ''
    
    try:
        sale_price = sp.find_element(By.CLASS_NAME, 'sale-price').text.strip()
    except: sale_price = ''
        
    current_price = ''
    if not sale_price and not original_price:
        try:
            current_price = sp.find_element(By.CLASS_NAME, 'product-price').text.strip()
        except:
            current_price = ''

    if name:
        stt.append(i)
        ten_san_pham.append(name)
        gia_goc.append(original_price)
        gia_km.append(sale_price)
        gia_ban_cuoi = sale_price if sale_price else current_price
        gia_ban.append(gia_ban_cuoi)
        
        try:
            img = sp.find_element(By.TAG_NAME, 'img').get_attribute('src')
        except: img = ''
        hinh_anh.append(img)
        
        print(f"  {i}. Tên: {name} | Giá Bán: {gia_ban_cuoi}")


# ----------------------------
# 6. Xử lý dữ liệu và lưu ra Excel (Phần đã được sửa)
# ----------------------------
df = pd.DataFrame({
    "STT": stt,
    "Tên sản phẩm": ten_san_pham,
    "Giá gốc": gia_goc,
    "Giá khuyến mãi": gia_km,
    "Giá bán cuối": gia_ban,
    "Hình ảnh": hinh_anh
})

# Dùng engine='xlsxwriter' vì đã cài đặt thư viện này ở Bước 2
df.to_excel("gochek_sanpham.xlsx", index=False, engine='xlsxwriter') 

print("\n--- HOÀN TẤT ---")
print("Đã lưu dữ liệu ra gochek_sanpham.xlsx")
driver.quit()