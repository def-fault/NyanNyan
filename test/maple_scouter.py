from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 웹 드라이버 경로를 지정
driver = webdriver.Chrome()

user = "아ship"
url = 'https://maplescouter.com/info?name=' + user
driver.get(url)

# 동적 데이터 로딩을 기다림 (예: 10초 기다림)
wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'flex')))

# 데이터 추출
combPW = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]')
combPW = combPW.text

convST = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[4]/div/div[3]/div[1]')
convST = convST.text

hexaST = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[5]/div/div[3]/div[1]')
hexaST = hexaST.text

img_element = driver.find_element(By.XPATH,'//*[@id="root"]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/img')
img_src = img_element.get_attribute('src')

print("유저 이름 : " + user)
print("전투력 : " + combPW)
print("환산 : " + convST)
print("헥사 : " + hexaST)
print("링크 : " + img_src)

# 웹 드라이버 종료
driver.quit()