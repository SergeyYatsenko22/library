import requests
from pathlib import Path
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import argparse
import sys
from time import sleep


def main():

    class raise_redirect(requests):
        def check_for_redirect(self):
            if self.history: raise requests.exceptions.HTTPError
            pass

    parser = argparse.ArgumentParser(description='Книги в каком диапазоне надо скачать')
    parser.add_argument('-s', '--start_id', help='Начальный номер книги на сайте',
                        default='1', type=int)
    parser.add_argument('-e', '--end_id', help='Конечный номер книги на сайте',
                        default='5', type=int)
    args = parser.parse_args()

    def parse_book_page(content):
        soup = BeautifulSoup(content.text, 'lxml')
        image = soup.find(class_='bookimage').find('img')['src']
        title_tag = soup.find('h1')
        title = title_tag.text.strip().replace('\xa0 ', '').split(' :: ')[0]
        author = title_tag.text.strip().replace('\xa0 ', '').split(' :: ')[1]
        genres = [genre.text for genre in soup.find('span', class_='d_book').find_all('a')]

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

    def download_txt(title, id=1, folder='books/'):
        file_name = f'{id}. {sanitize_filename(title)}.txt'

        with open(os.path.join(folder, file_name), 'wb') as file:
            file.write(response_book_downloading.content)

    def download_image(image, id=1, folder='images/'):
        response = requests.get(urljoin('https://tululu.org/', image))
        response.raise_for_status()

        file_name = f'{id}.jpg'
        with open(os.path.join(folder, file_name), 'wb') as file:
            file.write(response.content)

    # def check_for_redirect(response):
    #     if response.history: raise requests.exceptions.HTTPError
    #     pass

    Path('books').mkdir(parents=True, exist_ok=True)
    Path('images').mkdir(parents=True, exist_ok=True)

    for book_number in range(args.start_id, args.end_id + 1):
        payload = {'id': book_number}
        book_url = 'https://tululu.org/b'
        book_download_url = 'https://tululu.org/txt.php'

        while True:
            try:
                response_book = requests.get(f'{book_url}{book_number}/', allow_redirects=False)
                response_book.raise_for_status()
                break
            except requests.exceptions.ConnectionError:
                sleep(5)
                print("Ошибка соединения", file=sys.stderr)

        response_book = raise_redirect.get(f'{book_url}{book_number}/', allow_redirects=False)

        try:
            response_book.check_for_redirect()
        except requests.exceptions.HTTPError:
            print("Страницы не существует", file=sys.stderr)
            continue

        try:
            response_book.check_for_redirect()
        except requests.exceptions.HTTPError:
            print("Нет книги для скачивания на сайте", file=sys.stderr)
            continue

        response_book_downloading = raise_redirect.get(book_download_url, params=payload)
        response_book_downloading.raise_for_status()

        try:
            response_book_downloading.raise_redirect()
        except requests.exceptions.HTTPError:
            print("Нет книги для скачивания на сайте", file=sys.stderr)
            continue

        title_downloaded = parse_book_page(response_book)
        download_txt(title_downloaded['title: '], book_number)
        image_downloaded = parse_book_page(response_book)
        download_image(image_downloaded['image_url: '], book_number)


if __name__ == '__main__':
    main()
