from selenium import webdriver
from selenium.webdriver.common.by import By
import time

#khoi tao webdriver
driver = webdriver.Chrome()

#mo trang
url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22P%22"
driver.get(url)

#doi mot chut de trang tai
time.sleep(2)

#lay ra tat ca ca the ul
ul_tags= driver.find_elements(By.TAG_NAME, "ul")
print(len(ul_tags))

#chon the ul th 21
ul_painters= ul_tags[19] #list start with index=0

#lay ra tat ca <li> thuoc ul_painters
li_tags= ul_painters.find_elements(By.TAG_NAME, "li")

#tao danh sach cac url
links=[tag.find_element(By.TAG_NAME, "a").get_attribute("href") for tag in li_tags]

#tao danh sach cac url
titles= [tag.find_element(By.TAG_NAME,"a").get_attribute("title") for tag in li_tags]

#in ra url
for link in links:
    print(link)

#in ra title
for title in titles:
    print(title)

#dong webdrive
driver.quit()