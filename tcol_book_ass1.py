import os
import django
import uuid
import requests
import time
import csv
from requests.exceptions import HTTPError, RequestException

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tcol.settings')
django.setup()
from scraper.models import Book

LOC_API_URL = "https://www.loc.gov/books/"

GENRE_MAP = {
    'travel': 'Travel',
    'mystery': 'Mystery',
    'historical fiction': 'Historical Fiction',
    'comics': 'Sequential Art',
    'graphic novels': 'Sequential Art',
    'sequential art': 'Sequential Art',
    'classics': 'Classics',
    'philosophy': 'Philosophy',
    'romance': 'Romance',
    'science fiction': 'Science Fiction',
    'fantasy': 'Fantasy',
    'children': 'Childrens',
    'childrens': 'Childrens',
    'religion': 'Religion',
    'nonfiction': 'Nonfiction',
    'music': 'Music',
    'fiction': 'Fiction'
}

def normalize_genre(raw_genre):
    if not raw_genre:
        return "Default"
    raw_genre_lower = raw_genre.lower()
    for key, value in GENRE_MAP.items():
        if key in raw_genre_lower:
            return value
    return "Default"

def search_loc_books(query, max_records=500, page_size=100, max_pages=5):
    all_results = []
    total_hits = None
    page_count = 0

    for start in range(1, max_records + 1, page_size):
        page_count += 1
        if page_count > max_pages:
            print(f"Reached max_pages limit ({max_pages}). Stopping further requests.")
            break

        params = {
            'q': query,
            'fo': 'json',
            'c': page_size,
            's': start
        }

        try:
            response = requests.get(LOC_API_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if total_hits is None:
                total_hits = data.get('pagination', {}).get('total', 'unknown')
                print(f"Total records matching query: {total_hits}")

            results = data.get('results', [])
            if not results:
                print("No more results returned by API.")
                break

            all_results.extend(results)
            if len(all_results) >= max_records:
                break

            time.sleep(0.5)  # polite delay

        except HTTPError as e:
            print(f"HTTP error on page starting at {start}: {e}")
            print("Stopping further requests due to server error.")
            break
        except RequestException as e:
            print(f"Request error on page starting at {start}: {e}")
            print("Stopping further requests due to request error.")
            break

    return all_results[:max_records]

def parse_loc_record(record):
    title = record.get('title') or record.get('title_display') or 'No Title'

    authors = record.get('contributor') or record.get('creator') or []
    if isinstance(authors, list):
        author = ', '.join(authors).strip()
    else:
        author = authors.strip() if authors else ''

    raw_date = record.get('date') or record.get('date_created') or ''
    raw_date = raw_date.strip()
    if len(raw_date) == 10 and raw_date[4] == '-' and raw_date[7] == '-':
        publicationdate = raw_date
    elif len(raw_date) == 4 and raw_date.isdigit():
        publicationdate = f"{raw_date}-12-31"
    else:
        publicationdate = "2025-12-31"

    subjects = record.get('subject') or record.get('subject_topic') or []
    if isinstance(subjects, list):
        raw_genre = ', '.join(subjects)
    else:
        raw_genre = subjects or 'Default'
    genre = normalize_genre(raw_genre)

    images = record.get('image_url') or record.get('thumbnail') or []
    cover_url = ''
    if isinstance(images, list) and images:
        cover_url = images[0].strip()
    elif isinstance(images, str):
        cover_url = images.strip()
    else:
        cover_url = ''  # Always use empty string if not available

    identifiers = record.get('identifier') or []
    isbn = ''
    for ident in identifiers:
        if ident.startswith('urn:isbn:'):
            isbn = ident.replace('urn:isbn:', '')
            break
    if not isbn:
        isbn = str(uuid.uuid4())

    # Truncate fields to avoid DB errors
    title = title[:500]
    author = author[:500]
    genre = genre[:255]
    cover_url = cover_url[:500]
    isbn = isbn[:50]

    return {
        'title': title,
        'author': author,
        'publicationdate': publicationdate,
        'Genre': genre,
        'CoveimageUrl': cover_url,
        'isbn': isbn
    }

def save_book_to_db(book_data, book_id):
    Book.objects.create(
        bookID=book_id,
        isbn=book_data['isbn'],
        title=book_data['title'],
        author=book_data['author'],
        summary='',
        totalCopies=5,
        availabeCopies=5,
        publicationdate=book_data['publicationdate'],
        CoveimageUrl=book_data['CoveimageUrl'],
        Genre=book_data['Genre']
    )
    print(f"Saved bookID {book_id}: {book_data['title']} by {book_data['author']}")

def write_records_to_csv(records, filename='loc_books_records.csv'):
    if not records:
        print("No records to write to CSV.")
        return

    fieldnames = records[0].keys()

    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Wrote {len(records)} records to '{filename}'")

def export_books_to_csv(filename='books_export.csv'):
    books = Book.objects.all()
    if not books.exists():
        print("No books found in database to export.")
        return

    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['bookID', 'isbn', 'title', 'author', 'publicationdate', 'Genre', 'CoveimageUrl', 'totalCopies', 'availabeCopies']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for book in books:
            writer.writerow({
                'bookID': book.bookID,
                'isbn': book.isbn,
                'title': book.title,
                'author': book.author,
                'publicationdate': book.publicationdate,
                'Genre': book.Genre,
                'CoveimageUrl': book.CoveimageUrl,
                'totalCopies': book.totalCopies,
                'availabeCopies': book.availabeCopies
            })

    print(f"Exported {books.count()} books to '{filename}'")

def clean_invalid_covers():
    # Remove books with invalid or default cover URLs
    deleted_default = Book.objects.filter(CoveimageUrl__iexact="default").delete()
    deleted_empty = Book.objects.filter(CoveimageUrl="").delete()
    print(f"Deleted {deleted_default[0]} books with cover 'default', {deleted_empty[0]} books with empty cover.")

def main():
    search_term = "mystery"
    max_books = 500
    start_year = 1726
    end_year = 2025

    clean_invalid_covers()

    print(f"Searching LOC digitized books with query: '{search_term}', up to {max_books} records")
    records = search_loc_books(search_term, max_books)

    if not records:
        print("No records found for your query.")
        return

    # Parse all records first
    parsed_records = [parse_loc_record(record) for record in records]

    # Write all parsed records to CSV file before filtering/saving to DB
    csv_filename = 'loc_books_records.csv'
    write_records_to_csv(parsed_records, csv_filename)

    # Confirmation prompt before updating DB
    while True:
        confirm = input(f"CSV file '{csv_filename}' created. Do you want to proceed with updating the database? (y/n): ").strip().lower()
        if confirm == 'y':
            break
        elif confirm == 'n':
            print("Database update cancelled by user.")
            return
        else:
            print("Please enter 'y' or 'n'.")

    count_saved = 0
    book_id = 1  # 起始 bookID

    for book_data in parsed_records:
        pub_year_str = book_data['publicationdate'][:4]
        author = book_data['author']
        cover_url = book_data['CoveimageUrl']

        if pub_year_str.isdigit():
            pub_year = int(pub_year_str)
            if (
                start_year <= pub_year <= end_year
                and cover_url
                and cover_url.lower() != "default"
                and author
            ):
                save_book_to_db(book_data, book_id)
                count_saved += 1
                book_id += 100  # 每次遞增 100

    print(f"Saved {count_saved} books published between {start_year} and {end_year} with valid cover images and authors.")

    export_books_to_csv()

if __name__ == "__main__":
    main()
