import requests
from bs4 import BeautifulSoup

def fetch_books_data():
    url = 'https://play.google.com/store/search?q=english+fiction&c=books'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        books = []
        # Inspect the page structure to find the HTML elements containing book info
        # For example, books might be in divs with a certain class (you need to check the actual HTML)
        for book_div in soup.select('div[class*="some-book-class"]'):  # Replace with actual selector
            title = book_div.select_one('a[class*="title-class"]').get_text(strip=True)
            author = book_div.select_one('a[class*="author-class"]').get_text(strip=True)
            price = book_div.select_one('span[class*="price-class"]').get_text(strip=True)
            rating = book_div.select_one('div[class*="rating-class"]').get_text(strip=True)
            books.append({
                'title': title,
                'author': author,
                'price': price,
                'rating': rating,
            })
        return books
    else:
        return None
