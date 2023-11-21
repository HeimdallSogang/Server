import time
from io import BytesIO
import json
import os
import re
import PyPDF2
from dotenv import load_dotenv
from openai import OpenAI
import requests


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except Exception as e:
        print(f"Error on OpenAI client configuration: {e}")
        return None

    return client


def analyze_pdf(pdf_url, test=False):
    # get analysts from the first page
    first_page_text = read_pdf(pdf_url, from_page=1, to_page=1)
    analysts = get_analysts(first_page_text, test=test)

    # get negative points from all pages
    all_text = read_pdf(pdf_url)
    negative_points = get_negative_points(all_text, test=test)

    return {"writers": analysts, "negative points": negative_points}


def get_negative_points(text_list: list, test=False) -> list:
    client = get_openai_client()
    BASE_MESSAGE = [
        {
            "role": "system",
            "content": """
                The credibility of the reason is the most important. Use only the provided text to find the answers. 
                Respond in a format of list of strings. ex) ["hello", "world"]
                If you can't find the answer to the question, return an empty list [].
                Answer in Korean. 
            """,
        },
        {
            "role": "user",
            "content": """
                Read the following stock analysis report and find out the negative reasons to sell this stock. 
                Only gather data from the sentences and not the tables and graphs.
                Do not fake answers. 
            """,
        },
    ]

    ret = []
    for text in text_list:
        messages = BASE_MESSAGE + [
            {"role": "user", "content": str(text)},
        ]

        if test:
            print(f"Q: Get negative points from: {str(text)}")
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", messages=messages, temperature=0
            )
            answer = response.choices[0].message.content
            result = json.loads(answer)
        except Exception as e:
            print(f"Error while getting answer from GPT: {e}")
            result = []

        if isinstance(result, list):
            new_points = [str(e) for e in result]
            ret += new_points
            if test:
                print(f"New negative points: {new_points}")

    return ret


def get_analysts(text_list: list, test=False) -> list:
    client = get_openai_client()

    BASE_MESSAGE = [
        {
            "role": "system",
            "content": """
                Use only the provided text to find the answers. 
                Respond in a format of list of strings. ex) ["hello", "world"]
                If you can't find the answer to the question, return an empty list [].
            """,
        },
        {
            "role": "user",
            "content": """
                Read the following stock analysis report and find out the author of the report. 
                If there are multiple, find all of them. If not found, respond as an empty list.
            """,
        },
    ]

    ret = []
    for text in text_list:
        messages = BASE_MESSAGE + [{"role": "user", "content": str(text)}]

        if test:
            print(f"Q: Get analysts from: {str(text)}")

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", messages=messages, temperature=0
            )
            answer = response.choices[0].message.content
            result = json.loads(answer)
        except Exception as e:
            print(f"Error while getting answer from GPT: {e}")
            result = []

        if isinstance(result, list):
            new_analysts = [str(e) for e in result]
            ret += new_analysts
            if test:
                print(f"New analysts: {new_analysts}")

    return ret


def preprocessing(page_text):
    cleaned_text = re.sub(r"[\n\t]", " ", page_text)
    return cleaned_text


def read_pdf(pdf_url, from_page=1, to_page=-1, max_text_length=1800) -> list:
    pdf_response = requests.get(pdf_url)
    if pdf_response.status_code != 200:
        print(f"PDF download failed. Status code: {pdf_response.status_code}")
        return []

    try:
        pdf_data = BytesIO(pdf_response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_data)

        text_list = []
        temp = ""

        num_pages = len(pdf_reader.pages)
        if from_page <= 0:
            from_page = 1
        if to_page < 0 or to_page > num_pages:
            to_page = num_pages

        for page_number in range(from_page - 1, to_page):
            page = pdf_reader.pages[page_number]
            page_text = preprocessing(page.extract_text())
            temp += page_text
            while len(temp) >= max_text_length:
                text_list.append(temp[:max_text_length])
                temp = temp[max_text_length:]
        text_list.append(temp)

        return text_list
    except Exception as e:
        print(f"Error while reading PDF: {e}")
        return []


def test_analyze_pdf(pdf_url):
    start_time = time.time()

    result = analyze_pdf(pdf_url, test=True)
    print(result)

    end_time = time.time()
    print(f"Elapsed time: {end_time - start_time:.2f}s")


if __name__ == "__main__":
    pdf_urls = [
        # 삼성전자 리포트
        "https://ssl.pstatic.net/imgstock/upload/research/company/1699846357166.pdf"
        # "https://ssl.pstatic.net/imgstock/upload/research/company/1699234215528.pdf",
        # "https://ssl.pstatic.net/imgstock/upload/research/company/1698805833360.pdf",
        # "https://ssl.pstatic.net/imgstock/upload/research/company/1698803821224.pdf",
        # "https://ssl.pstatic.net/imgstock/upload/research/company/1698879199721.pdf",
    ]

    for pdf_url in pdf_urls:
        test_analyze_pdf(pdf_url)
