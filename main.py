import requests
from pathlib import Path
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename


def download_txt(url, filename, id=1, folder='books/'):

    responce = requests.get(url)
    responce.raise_for_status()

    file_name = f'{id}' + '. ' + sanitize_filename(filename)+".txt"
    with open (os.path.join(folder, file_name), 'wb') as file:
        file.write(responce.content)

    return os.path.join(folder, file_name)


def check_for_redirect(responce):
    if not responce.history:
        pass
    else:
        raise requests.exceptions.HTTPError


Path("books").mkdir(parents=True, exist_ok=True)

for book_number in range(1,11):
    payload = {'id': book_number}
    url_book = "https://tululu.org/b"
    url_book_download = "https://tululu.org/txt.php"

    responce_book_title = requests.get(f'{url_book}{book_number}')
    responce_book_title.raise_for_status()

    responce_book_download = requests.get(url_book_download, params=payload)
    responce_book_download.raise_for_status()

    try:
        check_for_redirect(responce_book_download)
    except requests.exceptions.HTTPError:
        continue

    soup = BeautifulSoup(responce_book_title.text, 'lxml')
    title_tag = soup.find('h1')
    title = title_tag.text.strip().replace('\xa0 ', '').split(' :: ')[0]
    print(title)


    download_txt(f'{url_book}{book_number}', title, book_number)



    # file_name = f'books/id{book_number}.txt'
    # with open (file_name, 'wb') as file:
    #     file.write(responce.content)



# https://tululu.org/txt.php?id=32168