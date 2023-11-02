from bs4 import BeautifulSoup
from requests_html import HTMLSession  
import requests
import os, tqdm, sys, json
from urllib.parse import urljoin, urlparse

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--u', type=str, required=True,
                    help='Starting URL to parse (e.g. http://main.com)')
parser.add_argument('-m', '--m', type=str, required=False,
                    help='XPath to look for main content (e.g. \'div.main\', \'div[id=\"main\"]\')')
parser.add_argument('-n', '--n', type=str, required=False,
                    help='XPath to look for site navigation links (e.g. \'div.nav a\')')
parser.add_argument('-js', '--js', type=str, required=False,
                    help='Whether to run JavaScript on page or not (0=False, 1=True (default))')

args = parser.parse_args()

START_PAGE = args.u
if START_PAGE is None:
    raise(Exception("Missing url to scrape, e.g. python main.py https://www.evas.ca"))


MAIN_TAG = args.m
NAV_TAG = args.n
RUN_JS = not not args.js
OUTPUT_DIR = './output/'

if RUN_JS:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    DRIVER = webdriver.Chrome(options=options)

def render_HTML(url):
    text = None
    try:
        if RUN_JS:
            DRIVER.get(url)
            text = DRIVER.page_source
    except:
        pass
    if text is None:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
        res = requests.get(url, headers=headers)
        text = res.text

    return text

def get_and_save_html(url: str, filepath: str):
    text = render_HTML(url)

    if not filepath.endswith('.html'):
        filepath += '.html'

    f = open(filepath, "w", encoding='utf-8')
    for line in text:
        f.write(line)
    f.close()
    return text


def get_page(url, filepath, search_tag=None):
    text = get_and_save_html(url, filepath)

    html_text = None
    if search_tag is not None:
        soup = BeautifulSoup(text, "html.parser")
        html_text = "\n".join([h.extract().get_text() for h in soup.select(search_tag)])
    if html_text is None:
        soup = BeautifulSoup(text, "html.parser")
        html_text = soup.get_text()

    f = open(f'{filepath}.txt', "w", encoding='utf-8')  # Creating txt File

    for line in html_text.split('\n'):
        line = line.strip(' \n\t')
        if line != '':
            f.write(line + '\n')

    f.close()
    return soup


def get_path(base_url: str, href: str):
    if (not href) or href[0] == '#':
        return

    if href[0] == '/':
        href = base_url + href
    elif not href.startswith('http'):
        href = base_url + '/' + href

    parsed_url = urlparse(href)

    return OUTPUT_DIR + '/' + parsed_url.hostname + '/' + parsed_url.path

def scrape(start_page, search_tag, nav_tag):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    main_page = get_page(start_page, './', search_tag=search_tag)
    if nav_tag is not None:
        links = main_page.select(nav_tag)
    else:
        links = main_page.findAll('a')
    for a in tqdm.tqdm(links):
        href = a.attrs.get('href')

        filepath = get_path(start_page, href)

        href_path = urljoin(start_page, href) 

        if not filepath or (not href_path.startswith(start_page)):
            continue
        dir_path = filepath[:filepath.rindex('/')]

        if filepath.endswith('/'):
            filepath += 'index'

        os.makedirs(dir_path, exist_ok=True)
        get_page(href_path, filepath, search_tag=search_tag)


if __name__ == '__main__':
    scrape(start_page=START_PAGE, search_tag=MAIN_TAG, nav_tag=NAV_TAG)

    try:
        DRIVER.quit()
    except:
        pass
