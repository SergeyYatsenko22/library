import requests
from pathlib import Path
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import argparse
import sys
from time import sleep
import json


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def parse_book_page(content):
    soup = BeautifulSoup(content.text, 'lxml')
    image_selector = '.bookimage img'
    image = soup.select(image_selector)[0]['src']

    title_selector = 'h1'
    title_tag = soup.select_one(title_selector)

    title = title_tag.text.strip().replace('\xa0 ', '').split(' :: ')[0]
    author = title_tag.text.strip().replace('\xa0 ', '').split(' :: ')[1]

    genres_selector = 'span.d_book a'
    genres = [genre.text for genre in soup.select(genres_selector)]

    comments_selector = '.texts'
    comments_parsed = soup.select(comments_selector)

    comments = [comment.text.split(')')[1] for comment in comments_parsed]

    book = {
        'title: ': title,
        'author: ': author,
        'genre: ': genres,
        'comments: ': comments,
        'image_url: ': image
    }

    return book


def download_txt(title, book_id, folder):
    payload = {'book_id': book_id}
    downloaded_book_url = 'https://tululu.org/txt.php'

    book_downloading_response = requests.get(downloaded_book_url,
                                             params=payload)
    book_downloading_response.raise_for_status()
    check_for_redirect(book_downloading_response)

    file_name = f'{book_id}-{sanitize_filename(title)}.txt'
    with open(os.path.join(folder, file_name), 'wb') as file:
        file.write(book_downloading_response.content)


def download_image(image, book_id, folder):

    response = requests.get(urljoin('https://tululu.org/', image))
    response.raise_for_status()

    file_name = f'{book_id}.jpg'
    with open(os.path.join(folder, file_name), 'wb') as file:
        file.write(response.content)


def get_books_urls(content):
    soup = BeautifulSoup(content.text, 'lxml')
    book_urls_selector = '.d_book'
    books = soup.select(book_urls_selector)
    books_urls = []
    for book in books:
        book_id_selector = 'a'
        book_id = book.select(book_id_selector)[0]['href']
        books_urls.append(urljoin('https://tululu.org/', book_id))
    return books_urls


def main():
    parser = argparse.ArgumentParser(description=
                                     'Управление параметрами парсинга')
    parser.add_argument('-s', '--start_page',
                        help='Начальная страница',
                        default=1, type=int)
    parser.add_argument('-e', '--end_page', help='Конечная страница',
                        default=6, type=int)

    parser.add_argument('-df', '--dest_folder',
                        help='Папка для скаченной информации',
                        default='folder')

    parser.add_argument('-txt', '--skip_txt', action='store_true',
                        help='Отмена скачивания текста книг')

    parser.add_argument('-img', '--skip_img', action='store_true',
                        help='Отмена скачивания обложек книг')

    args = parser.parse_args()

    if args.end_page < args.start_page:
        args.end_page = args.start_page

    path = args.dest_folder

    Path(path).mkdir(parents=True, exist_ok=True)

    books = []
    for page in range(args.start_page, args.end_page + 1):
        while True:
            try:
                page_response = requests.get(f'https://tululu.org/l55/{page}')
                page_response.raise_for_status()
                check_for_redirect(page_response)
                books_urls = get_books_urls(page_response)
                break
            except requests.exceptions.ConnectionError:
                sleep(5)
                print('Ошибка соединения', file=sys.stderr)
            except requests.exceptions.HTTPError:
                print('Нет страницы на сайте', file=sys.stderr)
                break

        for book_url in books_urls:
            while True:
                try:
                    book_response = requests.get(book_url)
                    book_response.raise_for_status()
                    check_for_redirect(book_response)
                    parsed_book = parse_book_page(book_response)
                    books.append(parsed_book)
                    book_id = ''.join(
                        [num for num in filter(lambda num:
                                               num.isnumeric(), book_url)]
                    )
                    if not args.skip_txt:
                        download_txt(parsed_book['title: '], book_id, path)
                    if not args.skip_img or parsed_book['image_url: '] \
                            != '/images/nopic.gif':
                        download_image(parsed_book['image_url: '],
                                       book_id, path)
                    break
                except requests.exceptions.ConnectionError:
                    sleep(5)
                    print('Ошибка соединения', file=sys.stderr)
                except requests.exceptions.HTTPError:
                    print('Нет книги на сайте', file=sys.stderr)
                    break

    with open(f'{path}/books_json', 'w', encoding='UTF8') as json_file:
        json.dump(books, json_file, ensure_ascii=False)


if __name__ == '__main__':
    main()
