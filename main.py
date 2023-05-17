import requests
from pathlib import Path


def check_for_redirect(responce):
    if not responce.history:
        pass



Path("books").mkdir(parents=True, exist_ok=True)
for book_number in range(1,11):
    payload = {'id': book_number}
    url = "https://tululu.org/txt.php"


    responce = requests.get(url, params=payload)
    responce.raise_for_status()

    try:
        check_for_redirect(responce)
    except requests.exceptions.HTTPError:
        raise

# https://tululu.org/txt.php?id=32168


    file_name = f'books/id{book_number}.txt'
    with open (file_name, 'wb') as file:
        file.write(responce.content)
