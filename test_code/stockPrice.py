from dotenv import load_dotenv
import os
import requests
import xml.etree.ElementTree as ET ## XML 데이터 파싱을 위한 패키지

load_dotenv()
stockPriceApiBaseurl = "http://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"


# 요청 파라미터 설정
params = {
    "serviceKey": os.getenv("STOCK_PRICE_SERVICE_KEY"),
    "numOfRows" : "365", ## 검색 일수
    "itmsNm": "LG이노텍", ## 종목 이름
    "beginBasDt" : "20230807", ## 검색 시작 날짜
    "endBasDt" : "20230919"    ## 검색 종료 날짜
}

# GET 요청 보내기
response = requests.get(stockPriceApiBaseurl, params=params)

print(response.url)


# 응답 확인
if response.status_code == 200:

    xml_data = response.content

    root = ET.fromstring(xml_data)

    # clpr 요소 추출
    basDt_elements = root.findall(".//basDt")
    clpr_elements = root.findall(".//clpr")

    startPrice = -1

    ## 지금은 hidden_sentiment가 SELL인 경우를 기준으로 로직 작성
    days_hit = 0
    days_missed = 0
    days_to_first_hit = 0
    days_to_first_miss = 0
    # clpr 값 출력
    for i in range(len(basDt_elements)-1, -1, -1):

        ## 첫번째 날이 기준 날이므로 기준 가격을 정함
        if (i == len(basDt_elements)-1):
            startPrice = int(clpr_elements[i].text)

        basDt_element = basDt_elements[i]
        clpr_element = clpr_elements[i]

        basDt_element = basDt_element.text
        clpr_value = int(clpr_element.text)

        ## 올랐을 경우
        if startPrice < clpr_value:
            priceStatus = "오름"

            if days_missed == 0:
                days_to_first_miss= len(basDt_elements)-1 - i

            days_missed += 1
            

        elif startPrice > clpr_value:
            priceStatus = "내림"

            if days_hit == 0:
                days_to_first_hit = len(basDt_elements)-1 - i

            days_hit += 1

        else:
            priceStatus = ""

        print(f"{basDt_element}의 종가 : {clpr_value} {priceStatus}")

    print(f"days_hit : {days_hit}")
    print(f"days_missed : {days_missed}")
    print(f"days_to_first_hit : {days_to_first_hit}")
    print(f"days_to_first_miss : {days_to_first_miss}")

else:
    print("요청 실패:", response.status_code)