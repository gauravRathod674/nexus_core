from patterns.observer.subject import Subject
from patterns.observer.observer import UserObserver
from models.users import LibraryUser, Role
from models.items import PrintedBook, ItemStatus
from datetime import datetime, timedelta


def main():
    # Setup: Create subject and attach observer
    notifier = Subject()
    user_observer = UserObserver()
    notifier.attach(user_observer)

    # Dummy user and item
    user = LibraryUser("Sourish", "sourish@lib.com", "hashedpass", Role.STUDENT)
    item = PrintedBook(
        title="Clean Code",
        authors=["Robert C. Martin"],
        isbn="ISBN123",
        genres=["Programming", "Software Engineering"],
        publication_year=2008,
        language="English",
        status=ItemStatus.RESERVED,
        shelf_location="A1"
    )

    # 1️⃣ Reservation available
    print(">>> Simulating: Reserved book now available")
    notifier.notify('reservation_available', user=user, item=item)

    # 2️⃣ Due date approaching (3 days from now)
    due_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    print(">>> Simulating: Due date approaching")
    notifier.notify('due_date_approaching', user=user, item=item, due_date=due_date)

    # 3️⃣ Book returned and user is next in line
    print(">>> Simulating: Book returned, user next in line")
    notifier.notify('book_returned_notify_next', user=user, item=item)

    # 4️⃣ Reservation expired
    print(">>> Simulating: Reservation expired")
    notifier.notify('reservation_expired', user=user, item=item)


if __name__ == "__main__":
    main()
