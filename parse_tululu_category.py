import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def parse_tululu_tutorial(content):
    soup = BeautifulSoup(content.text, 'lxml')
    # book_id = soup.find(class_='d_book').find('a')['href']
    # return book_id

    books = soup.find_all(class_='d_book')
    for book in books:
        book_id = book.find('a')['href']
        print(urljoin('https://tululu.org/', book_id))
    return books

page_response = requests.get('https://tululu.org/l55/')
page_response.raise_for_status()


book_id = parse_tululu_tutorial(page_response)
# book_url = urljoin('https://tululu.org/', book_id)

# print(book_url)
parse_tululu_tutorial(page_response)