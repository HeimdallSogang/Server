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
        print(f'Error on OpenAI client configuration: {e}')
        return None
    
    return client

def analyze_pdf(pdf_url):
    # get analysts from the first page
    first_page_text = read_pdf(pdf_url, from_page=1, to_page=1)[0]
    analysts = get_analysts(first_page_text)

    # get negative points from all pages
    all_text = read_pdf(pdf_url)
    negative_points = get_negative_points(all_text)

    return {
        "writers": analysts,
        "negative points": negative_points
    }


def get_negative_points(text: list) -> list:
    # Incomplete

    client = get_openai_client()
    messages = [
        {
            "role": "system",
            "content": 
            """
                If you can't find a value corresponding to the key, set it to empty list and return it
                Use only the provided text.
                Respond in a format of list of strings.
            """,
        },
        {
            "role": "user",
            "content": 
            """
                Read the following stock analysis report and find out the author of the report. 
                If there are multiple, find all of them. If not found, respond as an empty list.
            """, 
        },
        {
            "role": "user", 
            "content": str(text)
        },
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages, temperature=0
    )
    answer = response.choices[0].message.content
    result = json.loads(answer)

    pass

def get_analysts(text) -> list:
    client = get_openai_client()

    messages = [
        {
            "role": "system",
            "content": 
            """
                Use only the provided text to find the answers. 
                Respond in a format of list of strings.
                If you can't find the answer to the question, return an empty list. 
            """,
        },
        {
            "role": "user",
            "content": 
            """
                Read the following stock analysis report and find out the author of the report. 
                If there are multiple, find all of them. If not found, respond as an empty list.
            """, 
        },
        {
            "role": "user", 
            "content": str(text)
        },
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages, temperature=0
    )
    answer = response.choices[0].message.content
    result = json.loads(answer)
    
    ret = []
    if isinstance(result, list):
        ret = [str(e) for e in result]
    
    return ret


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
                    Read the following stock analysis report and find the following data sets.
                    Find out all the negative reasons to sell this stock from the report. Only gather data from the sentences and not the tables and graphs.
                    Find our the Author of the report. if it's multiple find all of them.
                    Find out which company the report is writing about.
                    Respond appropriately to the format.
                    Do not fake answers. IF not found, tell me that it was not found.
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
        result = json.loads(answer)
        if 'reasons' in result and 'writers' in result:
            if isinstance(result['reasons'], list) and isinstance(result['writers'], list):
                return json.loads(answer)
            
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
        if from_page <= 0: from_page = 1
        if to_page < 0 or to_page > num_pages: to_page = num_pages

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
        print(f'Error while reading PDF: {e}')
        return []
    
def test_analysis(pdf_url="https://ssl.pstatic.net/imgstock/upload/research/company/1695343870257.pdf"):
    load_dotenv()
    text_list = read_pdf(pdf_url)
    for text in text_list:
        print(text)
        try:
            result = analyze(text)
            print(result)
            print("\n\n\n\n")
        except Exception as e:
            print(e)