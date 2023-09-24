from decimal import Decimal
import os
import openai
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from reports.models import Analyst, Currency, Point, Report, Stock, Writes
from test_code.analyze import read_pdf


def get_price_on_publish(stock, date):
    # TODO: 어떤 주식이 어떤 날에 마감가가 얼마였는지 리턴
    # stock.name이나 stock.code가 채워져있을 것을 요구

    return 48000


def get_stock_code(stock_name):
    # TODO: 공개된 API 등 이용해서 stock name -> stock code 변환 실행

    conversion = {
        "삼성전자": "005930",
        "카카오": "035720",
        "현대차": "005380",
        "현대자동차": "005380",
        "네이버": "035420",
        "NAVER": "035420",
        "SK하이닉스": "000660",
    }
    try:
        stock_code = conversion[stock_name]
    except Exception as e:
        return None

    return stock_code


def text_to_date(date_string):
    # "yy.mm.dd"를 파이썬 날짜 객체로 변경한다.

    # we assume that '23' refers to 2023.
    date_string = "20" + date_string
    date_object = datetime.strptime(date_string, "%Y.%m.%d").date()

    return date_object


def analyze(text):
    # TODO: analyze_with_gpt() 도입
    # 정확한 형식을 지켜내는지, 답변 수준이 높은지, 답변이 정확한지 확인 필요

    return {
        "negative thoughts": [
            "부정 의견 1",
            "부정 의견 2",
        ],
        "writer": [
            "김이름",
            "홍길동",
        ],
    }

    # return analayze_with_gpt(text)


def get_hidden_sentiment(report, analysts):
    # 리포트와 리포트를 쓴 애널리스트의 목록을 받아 같은 종목에 관해 같은 애널리스트들이 쓴 가장 가까운 과거의 리포트를 찾아 목표가를 비교한다.
    # 목표가가 하향됐으면 'SELL', 유지 또는 상향됐으면 'BUY'로 설정한다.
    # 바로 다음의 리포트에도 같은 방식을 적용해 업데이트해준다.

    last_report = (
        Report.objects.filter(
            stock=report.stock,
            writes__analyst__in=analysts,
            publish_date__lt=report.publish_date,
        )
        .order_by("publish_date")
        .last()
    )

    print(f"last report of {report} is {last_report}")

    hidden_sentiment = ""
    if last_report:
        if last_report.target_price < report.target_price:
            hidden_sentiment = "BUY"
        else:
            hidden_sentiment = "SELL"

    next_report = (
        Report.objects.filter(
            stock=report.stock,
            writes__analyst__in=analysts,
            publish_date__gt=report.publish_date,
        )
        .order_by("publish_date")
        .first()
    )

    print(f"next report of {report} is {next_report}")

    if next_report:
        if report.target_price < next_report.target_price:
            next_report.hidden_sentiment = "BUY"
        else:
            next_report.hidden_sentiment = "SELL"

        next_report.save()

    return hidden_sentiment


def get_next_publish_date(report, analysts):
    # 리포트와 리포트를 쓴 애널리스트의 목록을 받아 같은 종목에 관해 같은 애널리스트들이 쓴 가장 가까운 과거의 리포트를 찾아 is_newest, next_publish_date를 바꿔준다.
    # 이 리포트의 바로 다음 리포트를 찾아 다음 리포트의 존재여부, 존재한다면 publish_date에 따라 is_newest, next_publish_date를 업데이트한다.

    last_report = (
        Report.objects.filter(
            stock=report.stock,
            writes__analyst__in=analysts,
            publish_date__lt=report.publish_date,
        )
        .order_by("publish_date")
        .last()
    )

    if last_report:
        last_report.is_newest = False
        last_report.next_publish_date = report.publish_date
        last_report.save()

    next_report = (
        Report.objects.filter(
            stock=report.stock,
            writes__analyst__in=analysts,
            publish_date__gt=report.publish_date,
        )
        .order_by("publish_date")
        .first()
    )

    if next_report:
        return next_report.publish_date
    else:
        return None


def analayze_with_gpt(text):
    # text -> GPT -> dict with keys: negative thoughts, analysts
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        messages = [
            {
                "role": "system",
                "content": "You will be provided some text from a stock report. Your task is to analyze this text, find out the name (or names) of the analyst wrote this report, extract negative thoughts, and respond appropriately to the format.",
            },
            {
                "role": "system",
                "content": "You should answer in JSON, with 'analysts' and 'negative thoughts' as keys. Values of each key should be a list of strings.",
            },
            {
                "role": "system",
                "content": "If the provided text does not contain the information needed, then set null as the value.",
            },
            {"role": "user", "content": f"{text}:"},
            {
                "role": "user",
                "content": "In the given text, find out negative thoughts, and names of analysts if provided.",
            },
        ]

        answer = ""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
        )
        answer = response["choices"][0]["message"]["content"]
        return answer
    except Exception as e:
        print(e)
        return ""


def get_report_detail_info(report_detail_page_url):
    # report_detail_page_url를 스크레이핑해 목표가, sentiment를 tuple에 담아 리턴

    response = requests.get(report_detail_page_url)
    soup = BeautifulSoup(response.text, "html.parser")

    target_price = None
    written_sentiment = None

    money_elem = soup.select_one("em.money")
    if money_elem is not None:
        text = money_elem.text.replace(",", "")  # remove comma
        target_price = float(text)

    comment_elem = soup.select_one("em.coment")  # 'coment' 오타 아님
    if comment_elem is not None:
        written_sentiment = comment_elem.text

    if target_price is not None and written_sentiment is not None:
        written_sentiment = written_sentiment.strip().upper()
        if written_sentiment in ["BUY", "매수", "OUTPERFORM"]:
            written_sentiment = "BUY"
        elif written_sentiment in ["SELL", "매도"]:
            written_sentiment = "SELL"
        else:
            written_sentiment = "HOLD"

        return (target_price, written_sentiment)

    return None


def fetch_stock_reports(stock_name, currency="KRW"):
    # Get stock code from stock name
    stock_code = get_stock_code(stock_name)
    if stock_code is None:
        return None

    # Create and save Stock instance
    try:
        currency_instance = Currency.objects.get(code=currency.upper())
    except Currency.DoesNotExist:
        print(
            f"Currency with code: {currency} does not exists in database(Unsupported currency yet)"
        )
        return None
    stock, _ = Stock.objects.get_or_create(
        name=stock_name, code=stock_code, currency=currency_instance
    )

    page_num = 1

    while True:
        url = f"https://finance.naver.com/research/company_list.naver?keyword=&brokerCode=&writeFromDate=&writeToDate=&searchType=itemCode&itemCode={stock_code}&page={page_num}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the reports table
        reports_table = soup.select_one("div#contentarea table")

        # Iterate over each row in the table body (skipping header and empty rows)
        for row in reports_table.find_all("tr"):
            columns = row.find_all("td")

            # Skip if it's an empty row or header
            if not columns or len(columns) < 6:
                continue

            report_url_elem = columns[1].find("a")
            report_detail_page_url = (
                "https://finance.naver.com/research/" + report_url_elem["href"]
                if report_url_elem
                else None
            )

            report_title = report_url_elem.text if report_url_elem else None

            analyst_company = columns[2].text.strip()

            file_url_elem = columns[3].find("a")
            report_url = file_url_elem["href"] if file_url_elem else None

            publish_date_text = columns[4].text.strip()
            publish_date = text_to_date(publish_date_text)

            # check if report already in DB: report with same title and publish date is considered same report
            if Report.objects.filter(
                title=report_title, publish_date=publish_date
            ).exists():
                continue

            negative_points = []
            analyst_names = set()
            text_per_page = read_pdf(report_url)
            for text in text_per_page:
                analysis = analyze(text)
                for neg_point in analysis["negative thoughts"]:
                    negative_points.append(neg_point)
                for analyst in analysis["writer"]:
                    analyst_names.add(analyst)

            report_detail = get_report_detail_info(report_detail_page_url)
            if report_detail is None:
                break

            target_price, written_sentiment = report_detail
            target_price = Decimal(target_price)

            # report object with missing hidden_sentiment, is_newest, next_publish_date
            report = Report(
                title=report_title,
                stock=stock,
                url=report_url,
                target_price=target_price,
                publish_date=publish_date,
                written_sentiment=written_sentiment,
                price_on_publish=get_price_on_publish(stock, publish_date),
            )

            # save analaysts to DB
            try:
                analyst_list = []
                for name in analyst_names:
                    analyst, _ = Analyst.objects.get_or_create(
                        name=name, company=analyst_company
                    )
                    analyst_list.append(analyst)
            except Exception as e:
                print(f"Exception on saving analysts: {analyst}")
                print(e)
                break

            hidden_sentiment = get_hidden_sentiment(
                report=report, analysts=analyst_list
            )
            next_publish_date = get_next_publish_date(
                report=report, analysts=analyst_list
            )

            report.hidden_sentiment = hidden_sentiment
            report.is_newest = next_publish_date is None
            report.next_publish_date = next_publish_date

            # save report to DB
            try:
                report.save()
            except Exception as e:
                print(f"Exception on saving report: {report}")
                print(e)
                break

            # connect analaysts and report on DB
            try:
                for analyst in analyst_list:
                    Writes.objects.get_or_create(report=report, analyst=analyst)
            except Exception as e:
                print(f"Exception on saving 'Writes': {report} {analyst}")
                print(e)
                break

            # save negative points on DB
            try:
                point_list = []
                for neg_point in negative_points:
                    point, _ = Point.objects.get_or_create(
                        content=neg_point, report=report, is_positive=False
                    )
                    point_list.append(point)
            except Exception as e:
                print(f"Exception on saving 'Point': {point}")
                print(e)
                break

            # Print results
            print(f"Saved report: {report}")
            print(f"By analysts: {analyst_list}")
            print(f"Points on report: {point_list}")

        # 다음 페이지 없음을 의미
        if not soup.select_one("table.Nnavi td.pgRR"):
            break

        page_num += 1  # go to next page
