from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

# -------------------------------
# 1️⃣ Cấu hình Firefox + geckodriver (CẦN ĐIỀN ĐƯỜNG DẪN THỰC TẾ)
# -------------------------------
gecko_path = r"D:\Program\lo\baitap_selenium\geckodriver.exe"  # Thay đổi
firefox_binary = r"C:\Program Files\Mozilla Firefox\firefox.exe"  # Thay đổi

service = Service(gecko_path)
options = Options()
options.binary_location = firefox_binary
options.headless = False

driver = webdriver.Firefox(service=service, options=options)

# -------------------------------
# 2️⃣ Mở trang Wikipedia
# -------------------------------
url = 'https://vi.wikipedia.org/wiki/Danh_s%C3%A1ch_tr%C6%B0%E1%BB%9Dng_%C4%91%E1%BA%A1i_h%E1%BB%8Dc_t%E1%BA%A1i_Th%C3%A0nh_ph%E1%BB%91_H%E1%BB%93_Ch%C3%AD_Minh'
driver.get(url)
time.sleep(3) # Chờ trang load

# -------------------------------
# 3️⃣ Thu thập dữ liệu từ bảng
# -------------------------------
stt = []
ten_truong = []
dia_chi = []
loai_hinh = []

# XPATH: Nhắm tới tất cả các dòng (tr) trong bảng chính (wikitable)
# Bỏ qua dòng tiêu đề (header row)
# Lưu ý: Có thể cần điều chỉnh nếu cấu trúc trang thay đổi.
try:
    # Tìm tất cả các dòng (tr) của bảng (wikitable)
    rows = driver.find_elements(By.XPATH, "(//table[@class='wikitable'])[1]/tbody/tr")
    print(f"Tìm thấy {len(rows) - 1} dòng dữ liệu (trừ tiêu đề).")

    for i, row in enumerate(rows):
        if i == 0:
            continue # Bỏ qua dòng tiêu đề

        # Các cột:
        # 1. Tên trường (Cột 1: td[1])
        # 2. Địa chỉ (Cột 3: td[3])
        # 3. Loại hình (Cột 4: td[4])
        
        # ⚠️ CHÚ Ý: Cột Hiệu trưởng và Email không có trong bảng này.
        try:
            # Lấy Tên Trường (Cột 1)
            tt = row.find_element(By.XPATH, "./td[1]").text
        except:
            tt = ''

        try:
            # Lấy Địa chỉ (Cột 3)
            dc = row.find_element(By.XPATH, "./td[3]").text
        except:
            dc = ''

        try:
            # Lấy Loại hình (Cột 4)
            lh = row.find_element(By.XPATH, "./td[4]").text
        except:
            lh = ''

        # Thêm vào list nếu có tên trường
        if tt:
            stt.append(len(stt) + 1)
            ten_truong.append(tt)
            dia_chi.append(dc)
            loai_hinh.append(lh)
            
except Exception as e:
    print(f"Lỗi khi cào dữ liệu: {e}")

# -------------------------------
# 4️⃣ Lưu dữ liệu ra Excel
# -------------------------------
df = pd.DataFrame({
    "STT": stt,
    "Tên trường": ten_truong,
    "Địa chỉ": dia_chi,
    "Loại hình": loai_hinh,
    # CÁC CỘT NÀY BỊ BỎ TRỐNG DO THIẾU DỮ LIỆU TỪ NGUỒN WIKIPEDIA
    "Email": ['' for _ in stt], 
    "Tên Hiệu trưởng": ['' for _ in stt]
})

df.to_excel('danh_sach_truong_dai_hoc_tphcm.xlsx', index=False)
print(f"Đã lưu dữ liệu {len(stt)} trường ra danh_sach_truong_dai_hoc_tphcm.xlsx")

# -------------------------------
# 5️⃣ Đóng trình duyệt
# -------------------------------
driver.quit()