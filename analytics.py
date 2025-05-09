from collections import Counter
from datetime import datetime
from utils.dummy_data import get_dummy_transactions, get_dummy_items


def most_borrowed_books(transactions, items):
    isbn_counter = Counter(tx.isbn for tx in transactions)
    isbn_to_title = {item.isbn: item.title for item in items}
    top_books = isbn_counter.most_common(5)

    print("\n Most Borrowed Books:")
    for isbn, count in top_books:
        print(f" - {isbn_to_title.get(isbn, 'Unknown')} (ISBN: {isbn}) - {count} times")


def peak_borrow_hours(transactions):
    hour_counter = Counter(tx.borrow_date.hour for tx in transactions)
    top_hours = hour_counter.most_common(3)

    print("\n Peak Borrowing Hours:")
    for hour, count in top_hours:
        label = f"{hour:02d}:00 - {hour:02d}:59"
        print(f" - {label}: {count} transactions")


def popular_genres(transactions, items):
    isbn_to_genres = {item.isbn: item.genres for item in items if hasattr(item, "genres")}
    genre_counter = Counter()

    for tx in transactions:
        genres = isbn_to_genres.get(tx.isbn, [])
        genre_counter.update(genres)

    top_genres = genre_counter.most_common(5)

    print("\n Most Popular Genres:")
    for genre, count in top_genres:
        print(f" - {genre}: {count} times")


def dashboard():
    transactions = get_dummy_transactions()
    items = get_dummy_items()

    while True:
        print("\n Nexus Library Analytics Dashboard")
        print("1. View Most Borrowed Books")
        print("2. View Peak Borrowing Hours")
        print("3. View Most Popular Genres")
        print("4. Exit")

        choice = input("Select an option [1-4]: ").strip()

        if choice == "1":
            most_borrowed_books(transactions, items)
        elif choice == "2":
            peak_borrow_hours(transactions)
        elif choice == "3":
            popular_genres(transactions, items)
        elif choice == "4":
            print(" Exiting Dashboard.")
            break
        else:
            print(" Invalid option. Please try again.")


if __name__ == "__main__":
    dashboard()
