from dotenv import load_dotenv
from openai import OpenAI
import os
import requests
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO
import re
import json

## 커밋 테스트용 주석2
load_dotenv()


def analyze(text):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        messages = [
            {
                "role": "system",
                "content": 
                """
                    If you can't find a value corresponding to the key, set it to empty list and return it
                    The credibility of the reason is the most important.
                    Use only the provided text.
                    Respond in JSON format with 'reasons' and  'writers' and 'companies' as keys.
                    Answer in Korean
                """,
            },
            {
                "role": "user", "content": f"{text}:"
            },
            {
                "role": "user",
                "content": 
                """
                    Analyze this stock analysis.
                    Find out reasons to sell this stock.
                    Find out writers of this report, not the company they are working for.
                    Find out companies.
                    Respond appropriately to the format
                """,
            },
            {
                "role": "assistant",
                "content":
                """
                    {
                        "reasons": [
                        ],
                        "writers": [
                        ]
                        "companies": [
                        ]
                    }
                """
            }
        ]

        answer = ""
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=messages, temperature=0
        )
        answer = response.choices[0].message.content
        print(answer)
        result = json.loads(answer)
        if 'reasons' in result and 'writers' in result:
            if isinstance(result['reasons'], list) and isinstance(result['writers'], list):
                return json.loads(answer)
        print("fail")
        return {
            "reasons": [],
            "writers": [],
        }
    except Exception as e:
        print(e)
        return {
            "reasons": [],
            "writers": [],
        }


def preprocessing(page_text):
    cleaned_text = re.sub(r"[\n\t]", " ", page_text)
    return cleaned_text


def read_pdf(pdf_url):
    pdf_response = requests.get(pdf_url)
    if pdf_response.status_code != 200:
        print(f"PDF 다운로드에 실패하였습니다. 상태 코드: {pdf_response.status_code}")
    try:
        pdf_data = BytesIO(pdf_response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_data)
        num_pages = len(pdf_reader.pages)
        print(f"총 페이지 수: {num_pages}")
        text_list = []
        temp = ""
        max_length = 1800
        for page_number in range(num_pages):
            page = pdf_reader.pages[page_number]
            page_text = preprocessing(page.extract_text())
            temp += page_text
            while len(temp) >= 2000:
                text_list.append(temp[:max_length])
                temp = temp[max_length:]
        text_list.append(temp)
        return text_list
    except Exception as e:
        print(e)
        return ""


def crawl_pdf_link(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(response.status_code)
            return
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # 모든 <tr> 요소를 선택
        all_tr_elements = soup.find_all("tr")

        # 각 <tr> 요소를 순회하면서 원하는 데이터 추출
        for tr in all_tr_elements:
            stock_item = tr.find("a", class_="stock_item").text
            title = tr.find("td").find("a").text
            company_name = tr.find_all("td")[2].text
            print(stock_item)
            print(title)
            print(company_name)

        file_tds = soup.find_all("td", class_="file")
        soup = BeautifulSoup(html, "html.parser")

        # 모든 <tr> 요소를 선택
        all_tr_elements = soup.find_all("tr")

        # 각 <tr> 요소를 순회하면서 원하는 데이터 추출
        for tr in all_tr_elements:
            stock_item = tr.find("a", class_="stock_item").text
            title = tr.find("td").find("a").text
            company_name = tr.find_all("td")[2].text
            print(stock_item)
            print(title)
            print(company_name)

        file_tds = soup.find_all("td", class_="file")
        pdf_urls = []
        a_tag = soup.find("a", class_="stock_item")
        title = a_tag["title"]
        print(title)
        for file_td in file_tds:
            a_tag = file_td.find("a")
            pdf_url = a_tag["href"]
            a_tag = file_td.find("a")
            pdf_url = a_tag["href"]
            pdf_urls.append(pdf_url)
        return pdf_urls
    except Exception as e:
        print(e)
        return ""


if __name__ == "__main__":
    start_url = "https://finance.naver.com/research/company_list.naver?keyword=&brokerCode=&writeFromDate=&writeToDate=&searchType=itemCode&itemName=%C4%AB%C4%AB%BF%C0&itemCode=035720&x=40&y=33"
    for i in range(1, 10):
        url = f"{start_url}&page={i}"
        pdf_urls = crawl_pdf_link(url)
        for pdf_url in pdf_urls:
            print(pdf_url)
            pdf_url = "https://ssl.pstatic.net/imgstock/upload/research/company/1695343870257.pdf"
            text_list = read_pdf(pdf_url)
            for text in text_list:
                print(text)
                try:
                    result = analyze(text)
                    print(result)
                    print("\n\n\n\n")
                except Exception as e:
                    print(e)
                break
            break
        break

