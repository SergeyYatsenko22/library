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


def download_txt(title, id, folder='books/'):

    payload = {'id': id}
    downloaded_book_url = 'https://tululu.org/txt.php'

    book_downloading_response = requests.get(downloaded_book_url,
                                             params=payload)
    book_downloading_response.raise_for_status()
    check_for_redirect(book_downloading_response)

    file_name = f'{id}-{sanitize_filename(title)}.txt'
    with open(os.path.join(folder, file_name), 'wb') as file:
        file.write(book_downloading_response.content)


def download_image(image, id, folder='images/'):
    if image == '/images/nopic.gif':
        return

    response = requests.get(urljoin('https://tululu.org/', image))
    response.raise_for_status()

    # file_number = ''.join([num for num in filter(lambda num: num.isnumeric(), book_url)])
    # print(image)
    file_name = f'{id}.jpg'
    with open(os.path.join(folder, file_name), 'wb') as file:
        file.write(response.content)


def get_books_urls(content):
    soup = BeautifulSoup(content.text, 'lxml')
    books = soup.find_all(class_='d_book')
    books_urls=[]
    for book in books:
        book_id = book.find('a')['href']
        # print(urljoin('https://tululu.org/', book_id))
        books_urls.append(urljoin('https://tululu.org/', book_id))
    return books_urls


def main():

    Path('books').mkdir(parents=True, exist_ok=True)
    Path('images').mkdir(parents=True, exist_ok=True)

    books=[]

    for page in range (1, 5):
        page_response = requests.get(f'https://tululu.org/l55/{page}')
        page_response.raise_for_status()
        get_books_urls(page_response)

        for book_url in get_books_urls(page_response):
            # print(book_url)
            while True:
                try:
                    book_response = requests.get(book_url)
                    book_response.raise_for_status()
                    check_for_redirect(book_response)
                    break
                except requests.exceptions.ConnectionError:
                    sleep(5)
                    print("Ошибка соединения", file=sys.stderr)
                except requests.exceptions.HTTPError:
                    print("Нет книги на сайте", file=sys.stderr)
                    break

            # print(book_response)
            parsed_book = parse_book_page(book_response)
            books.append(parsed_book)

            # print(parsed_book['image_url: '])
            while True:
                try:
                    book_id = ''.join([num for num in filter(lambda num: num.isnumeric(), book_url)])
                    download_txt(parsed_book['title: '], book_id)
                    download_image(parsed_book['image_url: '], book_id)
                    break
                except requests.exceptions.ConnectionError:
                    sleep(5)
                    print("Ошибка соединения", file=sys.stderr)
                except requests.exceptions.HTTPError:
                    print("Нет книги для скачивания на сайте", file=sys.stderr)
                    break

    with open("books_json", "w", encoding="UTF8") as json_file:
        json.dump(books, json_file, ensure_ascii=False)

if __name__ == '__main__':
    main()