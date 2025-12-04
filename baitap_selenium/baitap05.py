from pygments.formatters.html import webify
from selenium import webdriver 
from selenium.webdriver.common.by import By
import time 
import pandas as pd
import re

#tao dataframe rong
d = pd.DataFrame({'name':[], 'birth':[], 'death':[], 'nationality':[]})

#khoi tao webdriver
driver= webdriver.Chrome()
 #mo trang
url= "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22P%22"
driver.get(url)

time.sleep(2)

try:
    name=driver.find_elements(By.TAG_NAME, "hi").text
except:
    name = ""
#ngay sinh
try:
    birth_element= driver.find_element(By.XPATH, "//th[text()='Born']/following-sibling::td")
    birth = birth_element.text
    birth= re.findall(r'[0-0](1,2)+\s+[A-Za-z]+\s+[0-9]{4}', birth)[0] #regex
except:
    birth = ""

#ngay mat
try:
    death_element= driver.find_element(By.XPATH, "//th[text()='Nationality']/following-sibling::td")
    death=death_element.textdeath=re.findall(r'[0-0](1,2)+\s+[A-Za-z]+\s+[0-9]{4}', birth)[0]
except:
    death=""

#lay ngay mat
try:
    nationality_element= driver.find_element(By.XPATH, "//th[text()='Nattionality']/following-sibling::td")
    nationality= nationality_element.text
except:
    nationality = ""

painter= {'name' : name, 'birth' : birth, 'death': death, 'nationality': nationality}

painter_df=pd.DataFrame([painter])

d=pd.concat([d, painter_df], ignore_index=True)

print(d)

driver.quit()