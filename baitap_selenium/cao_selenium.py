from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://vi.wikipedia.org/wiki/Danh_s%C3%A1ch_tr%C6%B0%E1%BB%9Dng_%C4%91%E1%BA%A1i_h%E1%BB%8Dc_t%E1%BA%A1i_Th%C3%A0nh_ph%E1%BB%91_H%E1%BB%93_Ch%C3%AD_Minh")
driver.maximize_window()
time.sleep(2)

rows = driver.find_elements(By.CSS_SELECTOR, "table.wikitable tbody tr")

schools = []

for r in rows[1:]:  # bỏ header
    cols = r.find_elements(By.TAG_NAME, "td")
    if len(cols) >= 2:
        name = cols[0].text.strip()
        address = cols[1].text.strip()
    else:
        continue

    schools.append({
        "Tên trường": name,
        "Địa chỉ": address,
        "Email": "NaN",
        "Hiệu trưởng": "NaN"
    })

driver.quit()

df = pd.DataFrame(schools)
df.to_csv("CaoDang_Wikipedia.csv", index=False, encoding="utf-8-sig")
print("Done!")
