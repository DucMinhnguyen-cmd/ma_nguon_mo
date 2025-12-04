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
gecko_path = r"D:\Program\lo\baitap_selenium\geckodriver.exe"  # Đường dẫn tới geckodriver.exe
firefox_binary = r"C:\Program Files\Mozilla Firefox\firefox.exe"  # Đường dẫn tới firefox.exe thực sự

# Tạo Service cho geckodriver
service = Service(gecko_path)

# Tạo Options
options = Options()
options.binary_location = firefox_binary
options.headless = False  # True nếu muốn chạy ẩn

# Khởi tạo WebDriver
driver = webdriver.Firefox(service=service, options=options)

# -------------------------------
# Mở trang web
# -------------------------------
url = 'https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/vitamin-khoang-chat'
driver.get(url)
time.sleep(2)  # Chờ trang load

# -------------------------------
#  Click "Xem thêm sản phẩm" nhiều lần
# -------------------------------
body = driver.find_element(By.TAG_NAME, "body")
time.sleep(1)

for _ in range(10):  # Lặp 10 lần click load thêm
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        clicked = False
        for button in buttons:
            if "Xem thêm" in button.text and "sản phẩm" in button.text:
                button.click()
                clicked = True
                time.sleep(1)  # Chờ nội dung load
                break
        if not clicked:
            break  # Không còn button "Xem thêm"
    except Exception as e:
        print(f"Lỗi khi click 'Xem thêm': {e}")
        break

# -------------------------------
#  Cuộn trang để load lazy-load
# -------------------------------
for _ in range(50):
    body.send_keys(Keys.ARROW_DOWN)
    time.sleep(0.05)  # Có thể tăng thời gian nếu trang chậm

time.sleep(1)  # Chờ trang load hết

# -------------------------------
#Thu thập dữ liệu sản phẩm
# -------------------------------
stt = []
ten_san_pham = []
gia_ban = []
hinh_anh = []

# Tìm tất cả button "Chọn mua"
buttons = driver.find_elements(By.XPATH, "//button[text()='Chọn mua']")
print(f"Tìm thấy {len(buttons)} sản phẩm")

for i, bt in enumerate(buttons, 1):
    parent_div = bt
    for _ in range(3):  # Quay ngược 3 thẻ cha để tới container sản phẩm
        parent_div = parent_div.find_element(By.XPATH, "./..")
    sp = parent_div

    # Lấy tên sản phẩm
    try:
        tsp = sp.find_element(By.TAG_NAME, 'h3').text
    except:
        tsp = ''

    # Lấy giá bán
    try:
        gsp = sp.find_element(By.CLASS_NAME, 'text-blue-5').text
    except:
        gsp = ''

    # Lấy hình ảnh
    try:
        ha = sp.find_element(By.TAG_NAME, 'img').get_attribute('src')
    except:
        ha = ''

    # Thêm vào list nếu có tên sản phẩm
    if tsp:
        stt.append(i)
        ten_san_pham.append(tsp)
        gia_ban.append(gsp)
        hinh_anh.append(ha)

# -------------------------------
# Lưu dữ liệu ra Excel
# -------------------------------
df = pd.DataFrame({
    "STT": stt,
    "Tên sản phẩm": ten_san_pham,
    "Giá bán": gia_ban,
    "Hình ảnh": hinh_anh
})

df.to_excel('danh_sach_sp.xlsx', index=False)
print("Đã lưu dữ liệu ra danh_sach_sp.xlsx")


driver.quit()