import requests
from bs4 import BeautifulSoup
import re

# 웹 페이지에서 데이터 크롤링
url = "https://www.koreabaseball.com/Record/Crowd/GraphDaily.aspx"
data = []
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')
table = soup.find('table')

# 테이블의 tbody에서 데이터 추출
for row in table.find_all('tbody'):
    columns = row.find_all('td')
    for col in columns:
        # 텍스트 추출 및 정리
        cleaned_data = col.text.strip()
        cleaned_data = re.sub(r'<[^>]+>', '', cleaned_data)  # HTML 태그 제거
        cleaned_data = ' '.join(cleaned_data.split())  # 여분의 공백 제거
        data.append(cleaned_data)

# 데이터에서 날짜 형식 변경
def format_date(date_str):
    # 날짜 형식이 'YYYY/MM/DD'로 되어있으면 'YYYY.M.D'로 변환
    match = re.match(r'(\d{4})/(\d{2})/(\d{2})', date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}.{int(month)}.{int(day)}"  # 월과 일을 정수로 변환하여 '03'을 '3'으로 변경
    return date_str

# 각 데이터 항목을 확인하고 날짜 형식을 변환
formatted_data = [format_date(item) for item in data]

print(formatted_data)

from datetime import date, timedelta

# 올해 연도 가져오기
year = date.today().year

# 시작 날짜와 끝 날짜 설정
start_date = date(year, 3, 23)
end_date = date(year, 8, 24)

# 날짜 리스트 초기화
date_list = []

# 날짜 리스트에 날짜 추가
current_date = start_date
while current_date <= end_date:
    date_list.append(current_date)
    current_date += timedelta(days=1)

# 월요일과 7월 5,6,7일 제외
filtered_dates = [
    d for d in date_list
    if d.weekday() != 0 and d not in [date(year, 7, 5), date(year, 7, 6), date(year, 7, 7)]
]

# 날짜를 YYYY.M.D 형식으로 변환
def format_date(d):
    # 날짜 형식을 YYYY.M.D로 변환
    return f"{d.year}.{d.month}.{d.day}"

formatted_dates = [format_date(d) for d in filtered_dates]
print(formatted_dates)

from collections import defaultdict
from datetime import datetime

# 각 팀의 홈 지역 설정
team_locations = {
    'LG': '서울', 'KT': '수원', 'SSG': '인천', 'NC': '창원', '두산': '서울',
    'KIA': '광주', '롯데': '부산', '삼성': '대구', '한화': '대전', '키움': '서울'
}


# 이동 거리 계산 함수
def calculate_distance(loc1, loc2):
    distances = {
        ('서울', '수원'): 30, ('서울', '인천'): 40, ('서울', '창원'): 400, ('서울', '광주'): 300,
        ('서울', '부산'): 400, ('서울', '대구'): 300, ('서울', '대전'): 150, ('서울', '서울'): 0,
        ('수원', '인천'): 50, ('수원', '창원'): 370, ('수원', '광주'): 270,
        ('수원', '부산'): 350, ('수원', '대구'): 290, ('수원', '대전'): 140,
        ('인천', '창원'): 420, ('인천', '광주'): 340, ('인천', '부산'): 420, ('인천', '대구'): 330,
        ('인천', '대전'): 160, ('창원', '광주'): 190, ('창원', '부산'): 80, ('창원', '대구'): 90,
        ('창원', '대전'): 250, ('광주', '부산'): 200, ('광주', '대구'): 150, ('광주', '대전'): 160,
        ('부산', '대구'): 100, ('부산', '대전'): 230, ('대구', '대전'): 130
    }
    return distances.get((loc1, loc2)) or distances.get((loc2, loc1)) or 0


# 6일간 누적 데이터를 계산하는 함수
def calculate_stats(data, start_date, end_date):
    team_stats = defaultdict(lambda: {'home_games': 0, 'away_games': 0, 'total_audience': 0, 'away_distance': 0})

    # start_date와 end_date는 문자열 형식으로 전달됨
    start_date_obj = datetime.strptime(start_date, '%Y.%m.%d').date()
    end_date_obj = datetime.strptime(end_date, '%Y.%m.%d').date()

    for i in range(0, len(data), 6):
        date_str, day, home_team, away_team, location, audience = data[i:i + 6]

        date_obj = datetime.strptime(date_str, '%Y.%m.%d').date()

        if start_date_obj <= date_obj <= end_date_obj:
            audience = int(audience.replace(',', ''))  # 쉼표 제거 후 정수형으로 변환

            # 홈 팀 처리
            team_stats[home_team]['home_games'] += 1
            team_stats[home_team]['total_audience'] += audience

            # 어웨이 팀 처리
            team_stats[away_team]['away_games'] += 1
            # 모든 어웨이 경기에서 이동 거리 계산
            home_loc = team_locations[home_team]
            away_loc = team_locations[away_team]
            distance = calculate_distance(home_loc, away_loc)
            team_stats[away_team]['away_distance'] += distance

    result = {}
    for team, stats in team_stats.items():
        avg_audience = stats['total_audience'] / stats['home_games'] if stats['home_games'] > 0 else 0
        result[team] = {
            'team': team,
            'home_games': stats['home_games'],
            'away_games': stats['away_games'],
            'avg_audience': avg_audience,
            'away_distance': stats['away_distance']
        }

    return result


# 날짜를 'YYYY.M.D' 형식으로 변환하는 함수
def format_date_to_YMD(date_obj):
    return f"{date_obj.year}.{date_obj.month}.{date_obj.day}"


# 6일 단위로 결과를 계산하는 반복문
all_results = []

for i in range(len(formatted_dates) - 5):
    start_date = formatted_dates[i]  # 시작 날짜
    end_date = formatted_dates[i + 5]  # 6일 후 날짜

    result = calculate_stats(formatted_data, start_date, end_date)

    if not result:
        print(f"No data available for the period {start_date} to {end_date}.")
        continue

    all_results.append({
        'start_date': start_date,
        'end_date': end_date,
        'result': result
    })

# 각 결과 출력
for period_result in all_results:
    print(f"기간: {period_result['start_date']} ~ {period_result['end_date']}")
    for team, stats in period_result['result'].items():
        print(f"  {team}: 홈 경기 수 {stats['home_games']}, 어웨이 경기 수 {stats['away_games']}, "
              f"평균 관중수 {stats['avg_audience']:.0f}, 이동 거리 {stats['away_distance']} km")
    print()

import pandas as pd

# CSV 파일 불러오기
df = pd.read_csv("홈어웨이 데이터 추가.csv")

# 새로운 컬럼을 초기화 (float형으로 변환)
df['홈 경기수'] = df.get('홈 경기수', 0)
df['어웨이 경기수'] = df.get('어웨이 경기수', 0)
df['평균 관중수'] = df.get('평균 관중수', 0.0)  # 평균 관중수를 float형으로 초기화
df['평균 이동거리'] = df.get('누적 이동거리', 0.0)  # 이동거리도 float형으로 초기화

# 데이터를 각 팀과 날짜 범위에 맞춰 CSV에 추가
for period_result in all_results:
    start_date = period_result['start_date']
    end_date = period_result['end_date']

    for team, stats in period_result['result'].items():
        # 팀과 날짜 범위가 일치하는 행을 찾음
        mask = (
                (df['팀명'] == team) &
                (df['Start Date'].astype(str) <= end_date) &
                (df['End Date'].astype(str) >= start_date)
        )

        # 일치하는 행을 업데이트
        if df[mask].empty:
            print(f"No matching rows found for team {team} from {start_date} to {end_date}")
        else:
            df.loc[mask, '홈 경기수'] = stats['home_games']
            df.loc[mask, '어웨이 경기수'] = stats['away_games']
            df.loc[mask, '평균 관중수'] = stats['avg_audience']
            df.loc[mask, '누적 이동거리'] = stats['away_distance']
            print(f"Updated rows for team {team} from {start_date} to {end_date}:")
            print(df[mask])

# CSV 파일로 저장
df.to_csv("홈어웨이 데이터 추가.csv", index=False, encoding='utf-8-sig')
