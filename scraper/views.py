from django.shortcuts import render

# Create your views here.
from .utils import fetch_books_data

def books_list(request):
    books = fetch_books_data()
    return render(request, 'scraper/books_list.html', {'books': books})
