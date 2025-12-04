from builtins import range
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Khởi tạo Webdriver
driver = webdriver.Chrome()

# Duyệt qua các chữ cái từ A (65) đến Z (90)
for i in range(65, 91):
    url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22"+chr(i)+"%22"
    try:
        # Mở trang
        driver.get(url)

        # Đợi một chút để trang tải
        time.sleep(3)

        # Lay ra tat ca the ul
        ul_tags = driver.find_elements(By.TAG_NAME, "ul")
        print(len(ul_tags))

        # Chon the ul thu 21
        ul_painters = ul_tags[20] # list start with index=0

        # Lay ra tat ca the <li> thuoc ul_painters
        li_tags = ul_painters.find_elements(By.TAG_NAME, "li")

        # Tao danh sach cac url (Lấy title)
        titles = [tag.find_element(By.TAG_NAME, "a").get_attribute("title") for tag in li_tags]

        # In ra title
        for title in titles:
            print(title)
            
    except:
        print("Error!")

# Dong webdrive
driver.quit()

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time

# Đường dẫn đến file thực thi geckodriver
gecko_path = r"D:\Program\lo\baitap_selenium\geckodriver.exe"

# Khởi tạo đối tượng dịch vụ với đường geckodriver
ser = Service(gecko_path)

# Tạo tùy chọn Firefox đúng cách
options = Options()

# Đường dẫn đúng đến firefox.exe (KHÔNG dùng Firefox Installer)
options.binary_location = r"c:\\Program Files\\Mozilla Firefox\\firefox.exe"

# Hiển thị giao diện
options.headless = False

# Khởi tạo driver
driver = webdriver.Firefox(options=options, service=ser)

# Tạo url
url = 'http://pythonscraping.com/pages/javascript/ajaxDemo.html'

# Truy cập
driver.get(url)

# In ra nội dung của trang web
print("Before: ============================\n")
print(driver.page_source)

# Tạm dừng khoảng 3 giây
time.sleep(3)

# In lại
print("\n\n\nAfter: ============================\n")
print(driver.page_source)

# Đóng browser
driver.quit()