from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
from datetime import date, timedelta
import pandas as pd
import os

# ChromeDriver 설정
driver = webdriver.Chrome()

# 날짜 데이터 가져오기
year = date.today().year
start_date = date(year, 5, 29)
end_date = date(year, 6, 29)

# 날짜 리스트 생성
date_list = []
current_date = start_date

while current_date <= end_date:
    date_list.append(current_date)
    current_date += timedelta(days=1)

# 월요일과 7월 5, 6, 7일 제외
filtered_dates = [
    d for d in date_list
    if d.weekday() != 0 and d not in [date(year, 7, 5), date(year, 7, 6), date(year, 7, 7)]
]

# 날짜 문자열로 변환
string_dates = [d.strftime("%Y-%m-%d") for d in filtered_dates]

# URL 조합을 위한 기본 부분 (타격 데이터를 가져오는 예시)
url1 = "http://www.kbreport.com/teams/standard?rows=20&order=TPCT&orderType=DESC&teamId=&pitcher_type=&year_from=2024&year_to=2024&split01=day&split02_1="
url3 = "&split02_2="
url5 = "google_vignette"  # 팝업 제거

# 데이터 저장할 리스트
all_data = []
skipped_dates = []  # 타임아웃된 시작 날짜를 저장할 리스트

for i in range(len(string_dates) - 1):
    url2 = string_dates[i]
    url4 = string_dates[i]
    total_url = url1 + url2 + url3 + url4 + url5
    
    # 현재 처리 중인 날짜 구간 출력
    print(f"현재 처리 중: {url2} ~ {url4}")
    print("접속 중:", total_url)
    
    driver.get(total_url)

    try:
        WebDriverWait(driver, 200).until(
            EC.presence_of_element_located((By.ID, "resultListDiv"))
        )
        time.sleep(20)  # 동적 로딩 대기

        # 페이지 소스를 가져와서 BeautifulSoup으로 파싱
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 테이블 데이터 추출
        table = soup.find('table')

        if table:
            tbody = table.find('tbody')
            rows = tbody.find_all('tr')
            
            for row in rows:
                columns = row.find_all('td')
                row_data = [col.text.strip() for col in columns]
                # 해당 기간 추가
                row_data = [url2] + row_data
                all_data.append(row_data)

    except TimeoutException:
        print(f"Timeout: 페이지 로드 실패. 다음 URL로 이동합니다. (시작 날짜: {url2})")
        skipped_dates.append(url2)
        continue

driver.quit()

# 데이터프레임으로 변환
if all_data:
    df = pd.DataFrame(all_data)
    # 열 이름 지정 ("Start Date"와 나머지 열 이름)
    df.columns = ["Start Date"] + [f"Column {i}" for i in range(1, df.shape[1])]
    
    # CSV 파일 저장 경로 확인 및 설정
    file_path = "kbreport_data_daily.csv"
    try:
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        print(f"데이터가 '{file_path}' 파일로 저장되었습니다.")
    except Exception as e:
        print(f"CSV 파일 저장 중 오류 발생: {e}")
else:
    print("데이터가 수집되지 않았습니다.")

# 타임아웃된 날짜 출력
if skipped_dates:
    print("타임아웃된 시작 날짜 목록:")
    for date in skipped_dates:
        print(date)
else:
    print("타임아웃된 URL이 없습니다.")
