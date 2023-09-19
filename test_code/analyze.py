from dotenv import load_dotenv
import openai
import os
import requests
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO
import re
import json

## 커밋 테스트용 주석2
load_dotenv()
def analyze_view(text):
    try :
        openai.api_key = os.getenv("OPENAI_API_KEY")
        messages = [
            {"role": "system", "content": "Your role is to analyize this text, extract negative thoughts, and respond appropriately to the format."},
            {"role": "system", "content": "목표주가(target price), 작성자(writer) 또는 애널리스트(analyst)가 있다면 찾아줘, 없다면 null로 답을 줘"},
            {"role": "user", "content": "title: "},
            {"role": "user", "content": f"{text}:"},
            {"role": "user", "content": "Find out Negative thoughts in this text, and find target price, writer or analyst if there are."},
            {"role": "assistant", "content": "Could you give it in JSON format with 'negative thoughts' and 'target price' and 'writer' as keys?"},
            {"role" : "assistant", "content": "If you can't find a value corresponding to the key, set it to null and return it"},
        ]

        answer = ""
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = messages,
            temperature = 0,
        )
        answer = response['choices'][0]['message']['content']
        return answer
    except Exception as e :
        print(e)
        return ""


def preprocessing(page_text):
    cleaned_text = re.sub(r'[\n\t]', ' ', page_text)
    return cleaned_text


def read_pdf(pdf_url):
    pdf_response = requests.get(pdf_url)
    if pdf_response.status_code != 200:
        print(f'PDF 다운로드에 실패하였습니다. 상태 코드: {pdf_response.status_code}')
    try:
        pdf_data = BytesIO(pdf_response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_data)
        num_pages = len(pdf_reader.pages)
        print(f'총 페이지 수: {num_pages}')
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
        soup = BeautifulSoup(html, 'html.parser')
        file_tds = soup.find_all('td', class_='file')
        pdf_urls = []
        for file_td in file_tds:
            a_tag = file_td.find('a')
            pdf_url = a_tag['href']
            pdf_urls.append(pdf_url)
        return (pdf_urls)
    except Exception as e:
        print(e)
        return ""

start_url = 'https://finance.naver.com/research/company_list.naver?keyword=&brokerCode=&writeFromDate=&writeToDate=&searchType=itemCode&itemName=%C4%AB%C4%AB%BF%C0&itemCode=035720&x=40&y=33' 
for i in range(1, 10):
    url = f"{start_url}&page={i}"
    pdf_urls = crawl_pdf_link(url)
    for pdf_url in pdf_urls:
        print(pdf_url)
        text_list = read_pdf(pdf_url)
        for text in text_list:
            print(text + '\n\n\n\n')
            try:
                result = analyze_view(text)
                result = json.loads(result)
                print(result)
            except Exception as e:
                print(e)
            break
        break
    break


