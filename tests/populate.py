from datetime import datetime, timedelta

import requests

# Replace with FastAPI server URL
BASE_URL = "http://localhost:8081"

session = requests.Session()

books = [
    {"title": "Book One", "author": "Author A", "isbn": "007462542X", "published_year": 2020},
    {"title": "Book Two", "author": "Author B", "isbn": "978-0-596-52068-7", "published_year": 2021},
    {"title": "Book Three", "author": "Author C", "isbn": "0-596-52068-9", "published_year": 2022},
    {"title": "Book Four", "author": "Author D", "isbn": "9780596520687", "published_year": 2023},
]
patrons = [
    {"name": "John Doe", "email": "john.doe@gmail.com", "membership_start_date": datetime.utcnow().isoformat()},
    {"name": "Jane Doe", "email": "jane.doe@gmail.com", "membership_start_date": datetime.utcnow().isoformat()},
]

# Create books
book_ids = []
for book in books:
    response = session.post(f"{BASE_URL}/books/", json=book)
    response.raise_for_status()  # Raise an error if the request fails
    book_data = response.json()
    book_ids.append(book_data['id'])
    print(f"Created book: {book_data}")

# Create patrons
patron_ids = []
for patron in patrons:
    response = session.post(f"{BASE_URL}/patrons/", json=patron)
    response.raise_for_status()
    patron_data = response.json()
    patron_ids.append(patron_data['id'])
    print(f"Created patron: {patron_data}")

# Checkout two books
for i in range(2):
    book_id = book_ids[i]
    patron_id = patron_ids[i]
    checkout_url = f"{BASE_URL}/checkout/{book_id}/patron/{patron_id}"
    response = session.post(checkout_url, params={"checkout_period": 14})
    response.raise_for_status()
    book_data = response.json()
    print(f"Checked out book: {book_data}")

# Update book to make it overdue
now = datetime.utcnow()
thirty_days_ago = now - timedelta(days=30)
response = session.put(f"{BASE_URL}/books/{book_ids[0]}", json={"due_date": thirty_days_ago.isoformat()})
book_data = response.json()
print(f"Overdue book: {book_data}")

print("All operations completed successfully.")
