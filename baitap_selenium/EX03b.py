from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
import time
import pandas as pd

# Khởi tạo driver
driver = webdriver.Firefox()

# Tạo url
url = 'https://apps.lms.hutech.edu.vn/authn/login?next'

# Truy cập
driver.get(url)

# Tạm dừng khoảng 2 giây
time.sleep(2)

firstname_input = driver.find_element(By.ID, "emailOrUsername")
lastname_input = driver.find_element(By.ID, "password")

firstname_input.send_keys('nagato.minh@gmail.com')
time.sleep(1)
lastname_input.send_keys("Ducminh601")

time.sleep(2)
buttton = driver.find_element(By.ID, "sign-in")

buttton.click()
time.sleep(5)

driver.quit()