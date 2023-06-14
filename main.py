import requests
from pathlib import Path
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import argparse
import sys
from time import sleep


def parse_book_page(content):
    soup = BeautifulSoup(content.text, 'lxml')
    image = soup.find(class_='bookimage').find('img')['src']
    title_tag = soup.find('h1')
    title = title_tag.text.strip().replace('\xa0 ', '').split(' :: ')[0]
    author = title_tag.text.strip().replace('\xa0 ', '').split(' :: ')[1]
    genres = [genre.text for genre in soup.find('span', class_='d_book')
              .find_all('a')]

    comments_parsed = soup.find_all(class_='texts')

    comments = [comment.text.split(')')[1] for comment in comments_parsed]

    book = {
        'title: ': title,
        'author: ': author,
        'genre: ': genres,
        'comments: ': comments,
        'image_url: ': image
    }

    return book


def download_image(image, id=1, folder='images/'):
    response = requests.get(urljoin('https://tululu.org/',
                                    image))
    response.raise_for_status()

    file_name = f'{id}.jpg'
    with open(os.path.join(folder, file_name), 'wb') as file:
        file.write(response.content)


def download_txt(title, id=1, folder='books/'):
    payload = {'id': id}
    downloaded_book_url = 'https://tululu.org/txt.php'

    book_downloading_response = requests.get(downloaded_book_url,
                                             params=payload)
    book_downloading_response.raise_for_status()
    check_for_redirect(book_downloading_response)

    file_name = f'{id}. {sanitize_filename(title)}.txt'
    with open(os.path.join(folder, file_name), 'wb') as file:
        file.write(book_downloading_response.content)
    return True


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def main():
    parser = argparse.ArgumentParser(description='Книги в каком диапазоне'
                                                 ' надо скачать')
    parser.add_argument('-s', '--start_id',
                        help='Начальный номер книги на сайте',
                        default='1', type=int)
    parser.add_argument('-e', '--end_id', help='Конечный номер книги на сайте',
                        default='11', type=int)
    args = parser.parse_args()

    Path('books').mkdir(parents=True, exist_ok=True)
    Path('images').mkdir(parents=True, exist_ok=True)

    book_url = 'https://tululu.org/b'

    for book_number in range(args.start_id, args.end_id + 1):

        while True:
            try:
                book_response = requests.get(f'{book_url}{book_number}/')
                book_response.raise_for_status()
                check_for_redirect(book_response)
                break
            except requests.exceptions.ConnectionError:
                sleep(5)
                print("Ошибка соединения", file=sys.stderr)
            except requests.exceptions.HTTPError:
                print("Нет книги на сайте", file=sys.stderr)
                if book_number < (args.end_id + 1):
                    book_number += 1
                    continue
                else:
                    break

        parsed_book = parse_book_page(book_response)

        while True:
            try:
                download_txt(parsed_book['title: '], book_number)
                download_image(parsed_book['image_url: '], book_number)
                break
            except requests.exceptions.ConnectionError:
                sleep(5)
                print("Ошибка соединения", file=sys.stderr)
            except requests.exceptions.HTTPError:
                print("Нет книги для скачивания на сайте", file=sys.stderr)
                break


if __name__ == '__main__':
    main()
