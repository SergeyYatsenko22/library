import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError

def get_book_id(content):
    soup = BeautifulSoup(content.text, 'lxml')
    books = soup.find_all(class_='d_book')
    for book in books:
        book_id = book.find('a')['href']
        print(urljoin('https://tululu.org/', book_id))
    return books

page_response = requests.get('https://tululu.org/l55/')
page_response.raise_for_status()
get_book_id(page_response)

for page_id in range (1, 11):
    page_response = requests.get(f'https://tululu.org/l55/{page_id}')
    page_response.raise_for_status()
    get_book_id(page_response)


# book_id = parse_tululu_tutorial(page_response)
# book_url = urljoin('https://tululu.org/', book_id)

# print(book_url)
# parse_tululu_tutorial(page_response)



# цикл по всей библиотеке по жанру Научная фантастика
# while True:
#     page_response = requests.get(f'https://tululu.org/l55/{page_id}')
#     page_response.raise_for_status()
#     if not check_for_redirect(page_response):
#         parse_tululu_tutorial(page_response)
#         page_id += 1
#     else:
#         break