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

Path("books").mkdir(parents=True, exist_ok=True)
for book_number in range (32170, 32180):
    url = f"https://tululu.org/txt.php?id={book_number}"
    # print(url)

    responce = requests.get(url)
    responce.raise_for_status()
# https://tululu.org/txt.php?id=32168


    file_name = f'books/{book_number}.txt'
    with open (file_name, 'wb') as file:
        file.write(responce.content)
