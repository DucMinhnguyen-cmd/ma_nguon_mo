from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

# -------------------------------
# Cấu hình Firefox + geckodriver
# -------------------------------

gecko_path = r"D:\Program\lo\ma_nguon_mo\baitap_selenium\geckodriver.exe" 
firefox_binary = r"C:\\Program Files\\Mozilla Firefox\\firefox.exe"  

service = Service(gecko_path)
options = Options()
options.binary_location = firefox_binary
options.headless = False 

driver = webdriver.Firefox(service=service, options=options)

# -------------------------------
# Mở trang GOCHEK
# -------------------------------
url = "https://gochek.vn/"
driver.get(url)
time.sleep(3)

# =====================
# Click "Xem thêm" để load toàn bộ sản phẩm
# ----------------------------
for _ in range(10):
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            if "Xem thêm" in button.text:
                button.click()
                time.sleep(1)
                break
    except:
        break

# ----------------------------
# Cuộn trang để load sản phẩm lazy-load
# ----------------------------
body = driver.find_element(By.TAG_NAME, "body")
for _ in range(50):
    body.send_keys(Keys.ARROW_DOWN)
    time.sleep(0.05)
time.sleep(1)

# ----------------------------
# Thu thập thông tin sản phẩm
# ----------------------------
stt, ten_san_pham, gia_goc, gia_km, gia_ban, hinh_anh = [], [], [], [], [], []
products = driver.find_elements(By.CSS_SELECTOR, "div.product-item")  # selector chính xác với gochek

for i, sp in enumerate(products, 1):
    try: name = sp.find_element(By.TAG_NAME, 'h3').text
    except: name = ''
    try: original_price = sp.find_element(By.CLASS_NAME, 'original-price').text
    except: original_price = ''
    try: sale_price = sp.find_element(By.CLASS_NAME, 'sale-price').text
    except: sale_price = ''
    try: current_price = sp.find_element(By.CLASS_NAME, 'product-price').text
    except: current_price = ''
    try: img = sp.find_element(By.TAG_NAME, 'img').get_attribute('src')
    except: img = ''

    if name:
        stt.append(i)
        ten_san_pham.append(name)
        gia_goc.append(original_price)
        gia_km.append(sale_price)
        gia_ban.append(current_price)
        hinh_anh.append(img)

# ----------------------------
# Xử lý dữ liệu và lưu ra Excel
# ----------------------------
df = pd.DataFrame({
    "STT": stt,
    "Tên sản phẩm": ten_san_pham,
    "Giá gốc": gia_goc,
    "Giá khuyến mãi": gia_km,
    "Giá bán": gia_ban,
    "Hình ảnh": hinh_anh
})
df.to_excel("gochek_sanpham.xlsx", index=False)
print("Đã lưu dữ liệu ra gochek_sanpham.xlsx")
driver.quit()