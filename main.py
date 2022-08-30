from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse

START_PAGE = 'https://www.evas.ca'
OUTPUT_DIR = './output/'


def get_and_save_html(url: str, filepath: str):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
    res = requests.get(url, headers=headers)
    text = res.text

    if not filepath.endswith('.html'):
        filepath += '.html'

    f = open(filepath, "w", encoding='utf-8')
    for line in text:
        f.write(line)
    f.close()
    return text


def get_page(url, filepath, main_only=True):
    print(url, filepath)
    text = get_and_save_html(url, filepath)

    soup = BeautifulSoup(text, "html.parser")
    if main_only:
        html_text = soup.find('main').extract().get_text()
    else:
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
    path = parsed_url.path

    return OUTPUT_DIR + parsed_url.path


if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    main_page = get_page(START_PAGE, './')
    links = main_page.findAll('a')

    for a in links:
        href = a.attrs.get('href')

        filepath = get_path(START_PAGE, href)

        if not filepath or (START_PAGE not in href):
            continue

        dir_path = filepath[:filepath.rindex('/')]

        if filepath.endswith('/'):
            filepath += 'index'

        # print(f'{href} -> {filepath}(.html|.txt)')
        os.makedirs(dir_path, exist_ok=True)
        get_page(href, filepath)
