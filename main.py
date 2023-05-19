import requests
from pathlib import Path
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import urlparse, urlsplit


def download_txt(url, filename, id=1, folder='books/'):

    response = requests.get(url)
    response.raise_for_status()

    file_name = f'{id}' + '. ' + sanitize_filename(filename)+".txt"
    with open (os.path.join(folder, file_name), 'wb') as file:
        file.write(response.content)

    return os.path.join(folder, file_name)

def download_image(url, id=1, folder='images/'):
    link = urlparse('https://tululu.org/shots/9.jpg')
    response = requests.get(url)
    response.raise_for_status()

    file_name = f'{id}' + ".jpg"
    with open (os.path.join(folder, file_name), 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if not response.history:
        pass
    else:
        raise requests.exceptions.HTTPError


Path("books").mkdir(parents=True, exist_ok=True)
Path("images").mkdir(parents=True, exist_ok=True)

for book_number in range(1,11):
    payload = {'id': book_number}
    url_book = "https://tululu.org/b"
    url_book_download = "https://tululu.org/txt.php"

    response_book_title = requests.get(f'{url_book}{book_number}')
    response_book_title.raise_for_status()

    response_book_download = requests.get(url_book_download, params=payload)
    response_book_download.raise_for_status()

    try:
        check_for_redirect(response_book_download)
    except requests.exceptions.HTTPError:
        continue

    soup = BeautifulSoup(response_book_title.text, 'lxml')
    title_tag = soup.find('h1')
    title = 'Заголовок: ' + title_tag.text.strip().replace('\xa0 ', '').split(' :: ')[0]
    # print(title)
    image = soup.find(class_='bookimage').find('img')['src']
    print(urljoin('https://tululu.org/', image))
    image_url = urljoin('https://tululu.org/', image)

    # download_txt(f'{url_book}{book_number}', title, book_number)
    download_image(image_url, book_number)

    # link = urlparse('https://tululu.org/shots/9.jpg')
    # link1 = urlsplit('https://tululu.org/shots/9.jpg')
    # print(link)
    # print(link1)

    # https://tululu.org/shots/6.jpg


# https://tululu.org/txt.php?id=32168