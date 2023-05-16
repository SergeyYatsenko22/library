import requests
from pathlib import Path

# url = "https://dvmn.org/filer/canonical/1542890876/16/"
#
# responce = requests.get(url)
# responce.raise_for_status()
#
# file_name = 'dvm.svg'
# with open (file_name, 'wb') as file:
#     file.write(responce.content)
#
# def check_for_redirect:


Path("books").mkdir(parents=True, exist_ok=True)
for book_number in range(1,11):
    payload = {'id': book_number}
    url = "https://tululu.org/txt.php"

    # print(url)

    responce = requests.get(url, params=payload)
    responce.raise_for_status()
# https://tululu.org/txt.php?id=32168


    file_name = f'books/id{book_number}.txt'
    with open (file_name, 'wb') as file:
        file.write(responce.content)
