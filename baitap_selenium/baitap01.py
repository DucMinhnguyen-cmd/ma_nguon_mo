from pygments.formatters.html import webify
from selenium import webdriver
from selenium.webdriver.common.by import By
import time 

# khoi tao Webdriver 
driver = webdriver.Chrome()

# Mở full màn hình 
driver.maximize_window()

# mở trang 
url="https://en.wikipedia.org/wiki/List_of_painters_by_name"
driver.get(url)

# wait for 2secs
time.sleep(2)

# take all the <a>
tags = driver.find_elements(By.TAG_NAME, "a")

# make a list lien ket 
links = [tag.get_attribute("href") for tag in tags]

# xuat thong tin
for link in links:
    print(link)

# close webdriver
driver.quit()