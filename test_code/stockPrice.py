from dotenv import load_dotenv
import os
import requests
import xml.etree.ElementTree as ET ## XML 데이터 파싱을 위한 패키지
##from reports.models import *

load_dotenv()

def calculate_hit_rate_of_analyst():
    pass


def calculate_hit_rate_of_report():

    hidden_sentiment_db = "SELL"
    ## 적중률 계산에 필요한 DB 정보
    hidden_sentiment = -1 if hidden_sentiment_db == "SELL" else 1 ## 리포트에 숨겨진 정보
    is_newest = True          ## 가장 최신 리포트 여부
    itmsNm = "SK하이닉스"       ## 종목 이름
    beginBasDt = "20230807"   ## 리포트 발행 일자
    endBasDt = "20230924"     ## 리포트 유효기간

    stockPriceApiBaseurl = os.getenv("STOCK_PRICE_API_BASE_URL")

    ## 리포트가 가장 최신인 경우 : 유효기간은 1년으로 설정
    if is_newest:
        
        # 요청 파라미터 설정
        params = {
            "serviceKey": os.getenv("STOCK_PRICE_SERVICE_KEY"),
            "numOfRows" : "365", ## 검색 일수
            "itmsNm": itmsNm, ## 종목 이름
            "beginBasDt" : beginBasDt, ## 검색 시작 날짜
            "endBasDt" : endBasDt    ## 검색 종료 날짜
        }




    ## 리포트가 가장 최신이 아닌 경우 : 유효기간은 다음 리포트 공개날까지로 설정
    else:

        # 요청 파라미터 설정
        params = {
            "serviceKey": os.getenv("STOCK_PRICE_SERVICE_KEY"),
            "numOfRows" : "365", ## 검색 일수
            "itmsNm": itmsNm, ## 종목 이름
            "beginBasDt" : beginBasDt, ## 검색 시작 날짜
            "endBasDt" : endBasDt    ## 검색 종료 날짜
        }

    try:

        ## GET 요청 보내기
        response = requests.get(stockPriceApiBaseurl, params=params)

        # 응답 확인
        if response.status_code == 200:
            
            ## XML로 반환된 데이터의 내용 추출하기 위한 처리
            xml_data = response.content
            root = ET.fromstring(xml_data)

            # clpr(종가) 요소 추출
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

                ## 변화값 부호 * hidden_sentiment : 양수면 hit, 음수면 miss
                variance = (clpr_value - startPrice) * hidden_sentiment

                ## 맞췄을 경우
                if variance > 0:
                    priceStatus = "맞음!"

                    if days_hit == 0:
                        days_to_first_hit = len(basDt_elements)-1 - i

                    days_hit += 1


                elif variance < 0:
                    priceStatus = "--틀림!"

                    if days_missed == 0:
                        days_to_first_miss= len(basDt_elements)-1 - i

                    days_missed += 1

                else:
                    priceStatus = ""

                print(f"{basDt_element}의 종가 : {clpr_value} {priceStatus}")

            print(f"days_hit : {days_hit}")
            print(f"days_missed : {days_missed}")
            print(f"days_to_first_hit : {days_to_first_hit}")
            print(f"days_to_first_miss : {days_to_first_miss}")

        else:
            print("요청 실패:", response.status_code)



    except Exception as e:
        print(e)


calculate_hit_rate_of_report()