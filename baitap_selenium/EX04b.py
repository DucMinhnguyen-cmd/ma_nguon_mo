from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

# ====== THÔNG TIN TÀI KHOẢN ======
TUMBLR_EMAIL = "nagato.minh@gmail.com"
TUMBLR_PASSWORD = "Ducminh601@"

# ====== KHỞI TẠO SELENIUM ======
driver = webdriver.Chrome()

# 1️⃣ Vào trang login
driver.get("https://www.tumblr.com/login")
time.sleep(3)

# 2️⃣ Nhập email
email_input = driver.find_element(By.NAME, "email")
email_input.send_keys(TUMBLR_EMAIL)
time.sleep(3)

# 3️⃣ Nhập password
password_input = driver.find_element(By.NAME, "password")
password_input.send_keys(TUMBLR_PASSWORD)
password_input.send_keys(Keys.ENTER)
time.sleep(5)

print(" Đăng nhập thành công Tumblr!")

# 4️⃣ Truy cập Dashboard
driver.get("https://www.tumblr.com/dashboard")
time.sleep(5)

# Scroll để load nhiều bài hơn
for _ in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# 5️⃣ Lấy các bài trên dashboard
posts = driver.find_elements(By.CSS_SELECTOR, "article")

data = []

for p in posts[:5]:  # lấy 5 bài đầu tiên
    try:
        # lấy nội dung
        content = p.text.strip()
    except:
        content = "(không có nội dung)"

    try:
        # lấy link bài viết
        link = p.find_element(By.TAG_NAME, "a").get_attribute("href")
    except:
        link = ""

    try:
        # lấy tên blog (người đăng)
        blog_name = p.find_element(By.CSS_SELECTOR, "a[href*='/blog/']").text
    except:
        blog_name = "N/A"

    data.append({
        "blog": blog_name,
        "content": content,
        "link": link
    })

driver.quit()

# 6️⃣ Xuất file CSV
df = pd.DataFrame(data)
df.to_csv("tumblr_dashboard_posts.csv", index=False, encoding="utf-8")

print("🎉 Đã cào xong 5 bài từ Tumblr Dashboard!")
