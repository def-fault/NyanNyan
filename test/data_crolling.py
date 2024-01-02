import requests
from bs4 import BeautifulSoup

# 웹페이지 접속 및 HTML 가져오기
user = "아ship"
url = "https://maple.gg/u/" + user
response = requests.get(url)
html = response.text

# BeautifulSoup을 사용하여 HTML 파싱
soup = BeautifulSoup(html, 'html.parser')

# level = soup.find('span', class_='user-summary-level')
try:
    guild = soup.find('a', class_='text-yellow text-underline').text
except AttributeError:
    guild = "데이터 없음"

try:
    level = soup.find_all('li', class_='user-summary-item')[1].text
except IndexError:
    level= "데이터 없음"

world =  soup.find('li', class_='user-summary-item').text

try:
    job = soup.find_all('li', class_='user-summary-item')[2].text
except IndexError:
    job = "데이터 없음"


try:
    union = soup.find('span', class_='user-summary-level').text
except AttributeError:
    union = "데이터 없음"

try:
    floor = soup.find('h1', class_='user-summary-floor').text
    floor = floor.replace(" ", "")
    floor = floor.replace("\n", "")
except AttributeError:
    floor = "데이터 없음"
    floor = floor.replace("\n", "")


try:
    seed = soup.find_all('h1', class_='user-summary-floor')[1].text
    seed = seed.replace(" ", "")
    seed = seed.replace("\n", "")
except IndexError:
    seed = "데이터 없음"
    seed = seed.replace("\n", "")

try:
    score = soup.find_all('span', class_='user-summary-level')[1].text
    score = ''.join(char for char in score if char.isdigit())
    score = score + "점"
except IndexError:
    score = "데이터 없음"
    score = seed.replace("\n", "")


img_tag = soup.find('img', class_="character-image" )
image_src = img_tag.get('src')



'''
Rank_Comprehensive = soup.find('span', class_='row row-normal user-additional')
#Rank_Partitial = soup.find_all('span', class_='text-yellow text-underline')[1].text
#Job_Comprehensive = soup.find_all('span', class_='text-yellow text-underline')[1].text
#Job_Partitial = soup.find_all('span', class_='text-yellow text-underline')[1].text
'''

print("URL :", image_src)

print("레벨 :", level)
print("길드 :", guild)
print("월드 :", world)
print("직업 :", job)

print("유니온 :", union)
print("무릉 :", floor)
print("시드 :", seed)
print("업적 :", score)

'''
print("종합 랭킹")
print("전체 :", Rank_Comprehensive)
#("월드 :", Rank_Partitial)

print("월드 랭킹")
#print("전체 :", Job_Comprehensive)
#print("월드 :", Job_Partitial)

검색 정렬

레벨 : Lv.276  길드 : ships
직업 : 에반  월드 : 엘리시움

무릉 : 61층 유니온 : Lv.8114
시드 : 42층 업적 : 11670

종합 랭킹 
전체 : 58403위 월드 11904위
직업 랭킹
전체 : 932위 월드 175위

'''