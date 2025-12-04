from pygments.formatters.html import webify
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re

######################################################
# I. Tai noi chua links vaf Tao dataframe rong
all_links = []
d = pd.DataFrame({'name': [], 'birth': [], 'death': [], 'nationality': []})

######################################################
# II. Lay ra tat ca duong dan de truy cap den painters
# Khởi tạo Webdriver
for i in range(70, 71):
    driver = webdriver.Chrome()
    url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22"+chr(i)+"%22"
    try:
        
        # Mở trang
        driver.get(url)
        
        # Đợi một chút để trang tải
        time.sleep(3)
        
        # Lay ra tat cac ca the ul
        ul_tags = driver.find_elements(By.TAG_NAME, "ul")
        print(len(ul_tags))
        
        # Chon the ul thu 21
        ul_painters = ul_tags[20] # list start with index=0
        
        # Lay ra tat ca the <li> thuoc ul_painters
        li_tags = ul_painters.find_elements(By.TAG_NAME, "li")
        
        # Tao danh sach cac url
        links = [tag.find_element(By.TAG_NAME, "a").get_attribute("href") for tag in li_tags]
        for x in links:
            all_links.append(x)
    except:
        print("Error!")
        
    # Dong webdrive
    driver.quit()

# III. Lay thong tin cua tung hoa si
count = 0
driver = webdriver.Chrome() # Đưa ra ngoài vòng lặp để chỉ mở 1 lần

for link in all_links:
    if count > 3:
        break
    count = count + 1
    
    print(link)
    try:
        # Mo trang
        driver.get(link)
        time.sleep(2)
        
        # 1. Lay ten hoa si
        try:
            name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            name = ""
            
        # 2. Lay ngay sinh (Born)
        try:
            birth_element = driver.find_element(By.XPATH, "//th[text()='Born']/following-sibling::td")
            birth_raw = birth_element.text
            # Regex lay nam sinh
            birth = re.findall(r'\d{4}', birth_raw)[0] 
        except:
            birth = ""

        # 3. Lay ngay mat
        try:
            death_element = driver.find_element(By.XPATH, "//th[text()='Died']/following-sibling::td")
            death_raw = death_element.text
            # Regex lay nam mat
            death = re.findall(r'\d{4}', death_raw)[0]
        except:
            death = ""

        # 4. Lay quoc tich (Nationality)
        try:
            nationality_element = driver.find_element(By.XPATH, "//th[text()='Nationality']/following-sibling::td")
            nationality = nationality_element.text
        except:
            nationality = ""

        # Tao dictionary
        painter = {'name': name, 'birth': birth, 'death': death, 'nationality': nationality}
        
        # Them vao DataFrame
        painter_df = pd.DataFrame([painter])
        d = pd.concat([d, painter_df], ignore_index=True)

    except Exception as e:
        print(f"Error at {link}: {e}")

# Dong driver sau khi chay xong het vong lap
driver.quit()
# IV. In thong tin va luu file
print("\n" + "#"*40)
print("# KET QUA LAY DU LIEU:")
print("#"*40)
print(d)
# determining the name of the file
file_name = 'Painters.xlsx'

# saving the excel
d.to_excel(file_name)
print('\nDataFrame is written to Excel File successfully.')