import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import re
import os
import time

# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"}

# headers = {
#             "Content-Encoding": "gzip",
#             "Content-Security-Policy": "frame-ancestors 'self'",
#             "Content-Type" : "text/html;charset=utf-8",
#             "D-Cache": "from-cache",
#             "D-Geo" : "US",
#             "Link" : "<https://le-cdn.hibuwebsites.com/b74a5b9815144009b73881ebfa7bf523/dms3rep/multi/opt/borsheim-1920w.jpg>; rel=preload; as=image; fetchpriority=high",
#             "Server" : "ZENEDGE",
#             "Strict-Transport-Security":"max-age=31536000; preload",
#             "Transfer-Encoding":"chunked",
#             "Vary":"user-agent,accept-encoding",
#             "X-Cache-Status": "MISS",
#             "X-Cdn":"Served-By-Zenedge",
#             "X-Content-Type-Options":"nosniff",
#             "X-Frame-Options":"SAMEORIGIN",
#             "X-Zen-Fury":"0d74c818f1fe3c1e7616b149ab8b5b84dda224e4"
#         }


path = 'Results'


# remove special characters from the text

def remove_special_characters(text):
    # Newlines (replaced with space to preserve cases like word1\nword2)
    text = re.sub(r"\n+", " ", text)
    # Remove resulting ' '
    text = text.strip()
    text = re.sub(r'\s\s+', ' ', text)

    # emails
    text = re.sub('\S*@\S*\s?', '', text)

    # > Quotes
    text = re.sub(r'\"?\\?&?gt;?', '', text)

    # Bullet points/asterisk (bold/italic)
    text = re.sub(r'\*', '', text)
    text = re.sub('&amp;#x200B;', '', text)

    # remove the [removed] from text
    text = text.replace('[removed]', '')

    # remove the [deleted] from text
    text = text.replace('[deleted]', '')

    # things in parantheses or brackets
    text = re.sub(r'[\[.*?\]\(.*?\)]', '', text)

    # remove URLS
    text = re.sub(r'https?:\/\/.*[\r\n]*', '', text)

    # Strikethrough
    text = re.sub('~', '', text)

    # Exclamation mark remove
    text = re.sub('!', '', text)

    # Spoiler, which is used with < less-than (Preserves the text)
    text = re.sub('&lt;', '', text)
    text = re.sub(r'!(.*?)!', r'\1', text)

    # Code, inline and block
    text = re.sub('`', '', text)

    # Superscript (Preserves the text)
    text = re.sub(r'\^\((.*?)\)', r'\1', text)

    # Table
    text = re.sub(r'\|', ' ', text)
    text = re.sub(':-', '', text)

    text = re.sub('[{]+', "", text)
    text = re.sub('[}]+', "", text)
    # Heading
    text = re.sub('#', '', text)

    text = re.sub('"', '', text)

    text = re.sub('\'', '', text)
    text = re.sub(',', '', text)
    text = re.sub('`', '', text)
    text = re.sub(r'\n+', ' ', text).strip()
    text = re.sub(r'\t+', ' ', text).strip()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_data(directory):
    data_path = os.path.join(directory, 'links.csv')
    df = pd.read_csv(data_path)
    links = df['Links'].tolist()
    data = []
    try:
        req = requests.get(links[0], headers=headers)
        print(f'The link is {links[0]} and the status code is {req.status_code}')
        if req.status_code == 200:
            soup = bs(req.text, 'html.parser')
            text = soup.getText().lower()
            data.append(remove_special_characters(text))
            time.sleep(3)
    except Exception as e:
        print(e)
    for link in links[1:]:
        try:
            time.sleep(5)
            req = requests.get(link, headers=headers)
            print(f'The link is {link} and the status code is {req.status_code}')
            if req.status_code == 200:
                soup = bs(req.text, 'html.parser')
                # Find and remove header elements
                header = soup.find('header')
                if header:
                    header.extract()

                # Find and remove footer elements
                footer = soup.find('footer')
                if footer:
                    footer.extract()
                text = soup.getText().lower()
                data.append(remove_special_characters(text))

        except Exception as e:
            print(e)
    return data


for i in range(101, 150, 1):
    isExist = os.path.exists(os.path.join(path, str(i)))
    if isExist:
        directory = os.path.join(path, str(i))
        data = get_data(directory)
        df = pd.DataFrame(data, columns=['Data'])
        df.to_csv(os.path.join(directory, 'data.csv'), encoding="utf-8")
