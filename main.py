import requests
from pathlib import Path
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import argparse

parser = argparse.ArgumentParser(description="Книги в каком диапазоне надо скачать")
parser.add_argument('-s', '--start_id', help='Начальный номер книги на сайте',
                    default='1', type=int)
parser.add_argument('-e', '--end_id', help='Конечный номер книги на сайте',
                    default='5', type=int)
args = parser.parse_args()


def parse_book_page(content):
    soup = BeautifulSoup(content.text, 'lxml')
    title_tag = soup.find('h1')
    title = title_tag.text.strip().replace('\xa0 ', '').split(' :: ')[0]
    author = title_tag.text.strip().replace('\xa0 ', '').split(' :: ')[1]
    genres = [genre.text for genre in soup.find('span', class_='d_book').find_all('a')]

    book = {
        'Заголовок: ': title,
        'Автор: ': author,
        'Жанр: ': genres,
    }
    comments = soup.find_all(class_='texts')
    for comment in comments:
        book['Комментарии: '] = comment.text.split(')')[1]

    return book


def download_txt(content, id=1, folder='books/'):
    soup = BeautifulSoup(content.text, 'lxml')
    title_tag = soup.find('h1')
    title = title_tag.text.strip().replace('\xa0 ', '').split(' :: ')[0]
    payload = {'id': book_number}
    url_book_download = "https://tululu.org/txt.php"

    response_book_download = requests.get(url_book_download, params=payload)
    response_book_download.raise_for_status()

    file_name = f'{id}' + '. ' + sanitize_filename(title) + ".txt"

    with open(os.path.join(folder, file_name), 'wb') as file:
        file.write(response_book_download.content)


def download_image(content, id=1, folder='images/'):
    soup = BeautifulSoup(content.text, 'lxml')
    image = soup.find(class_='bookimage').find('img')['src']
    response = requests.get(urljoin('https://tululu.org/', image))
    response.raise_for_status()

    file_name = f'{id}' + ".jpg"
    with open(os.path.join(folder, file_name), 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if not response.history:
        pass
    else:
        raise requests.exceptions.HTTPError


Path("books").mkdir(parents=True, exist_ok=True)
Path("images").mkdir(parents=True, exist_ok=True)

for book_number in range(args.start_id, args.end_id + 1):
    payload = {'id': book_number}
    url_book = "https://tululu.org/b"
    url_book_download = "https://tululu.org/txt.php"

    response_book = requests.get(f'{url_book}{book_number}')
    response_book.raise_for_status()

    response_book_download = requests.get(url_book_download, params=payload)
    response_book_download.raise_for_status()

    try:
        check_for_redirect(response_book_download)
    except requests.exceptions.HTTPError:
        continue

    print(parse_book_page(response_book))
    download_txt(response_book, book_number)
    download_image(response_book, book_number)
