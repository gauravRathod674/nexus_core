from datetime import datetime, timedelta
from models.items import EBook, PrintedBook, ResearchPaper, Audiobook
from models.users import LibraryUser, Role
from models.notification import Notification
from models.reservation import Reservation, ReservationStatus
from models.transactions import BorrowingTransaction, TransactionStatus


def get_dummy_items():
    """
    Returns a list of dummy library items covering all types.
    """
    return [
        EBook(
            title="Deep Learning with Python",
            authors=["Francois Chollet"],
            isbn="9781617294433",
            file_format="PDF"
        ),
        EBook(
            title="Automate the Boring Stuff",
            authors=["Al Sweigart"],
            isbn="9781593275990",
            file_format="ePub"
        ),
        PrintedBook(
            title="Clean Code",
            authors=["Robert C. Martin"],
            isbn="9780132350884",
            shelf_location="A3-42"
        ),
        PrintedBook(
            title="The Pragmatic Programmer",
            authors=["Andrew Hunt", "David Thomas"],
            isbn="9780201616224",
            shelf_location="B1-15"
        ),
        ResearchPaper(
            title="Attention Is All You Need",
            authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
            isbn="10.48550/arXiv.1706.03762",
            journal="NeurIPS",
            year=2017
        ),
        ResearchPaper(
            title="ImageNet Classification with Deep Convolutional Neural Networks",
            authors=["Alex Krizhevsky", "Ilya Sutskever", "Geoffrey E. Hinton"],
            isbn="10.1145/3065386",
            journal="NIPS",
            year=2012
        ),
        Audiobook(
            title="The Hobbit",
            authors=["J.R.R. Tolkien"],
            isbn="9780261103344",
            duration_minutes=720
        ),
        Audiobook(
            title="1984",
            authors=["George Orwell"],
            isbn="9780451524935",
            duration_minutes=650
        )
    ]


def get_dummy_users():
    """
    Returns a list of dummy library users for each role.
    """
    return [
        LibraryUser(
            name="Alice Johnson",
            email="alice.johnson@example.com",
            password_hash="hash_alice",
            role=Role.STUDENT,
        ),
        LibraryUser(
            name="Bob Smith",
            email="bob.smith@example.com",
            password_hash="hash_bob",
            role=Role.RESEARCHER,
        ),
        LibraryUser(
            name="Dr. Carol Lee",
            email="carol.lee@example.edu",
            password_hash="hash_carol",
            role=Role.FACULTY,
        ),
        LibraryUser(
            name="Guest User",
            email="guest@example.com",
            password_hash="hash_guest",
            role=Role.GUEST,
        ),
        LibraryUser(
            name="Librarian Lucy",
            email="lucy.librarian@example.com",
            password_hash="hash_lucy",
            role=Role.LIBRARIAN,
            
        )
    ]


def get_dummy_notifications():
    """
    Returns a list of sample notifications for users.
    """
    now = datetime.now()
    return [
        Notification(
            user_name="Alice Johnson",
            message="Your loan for 'Deep Learning with Python' is due in 3 days.",
            timestamp=now - timedelta(days=1)
        ),
        Notification(
            user_name="Bob Smith",
            message="The item 'Attention Is All You Need' is now available for pickup.",
            timestamp=now - timedelta(hours=2)
        ),
        Notification(
            user_name="Dr. Carol Lee",
            message="Your reservation for 'The Pragmatic Programmer' is confirmed.",
            timestamp=now - timedelta(minutes=30)
        ),
        Notification(
            user_name="Guest User",
            message="As a guest, you cannot borrow items. Please register for full access.",
            timestamp=now - timedelta(days=2, hours=5)
        ),
        Notification(
            user_name="Librarian Lucy",
            message="System maintenance scheduled for tomorrow at 2 AM.",
            timestamp=now
        )
    ]


def get_dummy_reservations():
    """
    Returns a list of sample reservations for users.
    """
    now = datetime.now()
    res_list = [
        Reservation(
            user_name="Alice Johnson",
            isbn="9780132350884",
            reservation_date=now - timedelta(days=1)
        ),
        Reservation(
            user_name="Bob Smith",
            isbn="10.48550/arXiv.1706.03762",
            reservation_date=now - timedelta(days=3)
        ),
        Reservation(
            user_name="Dr. Carol Lee",
            isbn="9780201616224",
            reservation_date=now
        ),
        Reservation(
            user_name="Guest User",
            isbn="9780451524935",
            reservation_date=now - timedelta(hours=5)
        ),
        Reservation(
            user_name="Librarian Lucy",
            isbn="9780261103344",
            reservation_date=now - timedelta(days=2)
        )
    ]
    # expire/cancel some
    for res in res_list:
        if res.user_name == "Bob Smith":
            res.expire()
        if res.user_name == "Librarian Lucy":
            res.cancel()
    return res_list


def get_dummy_transactions():
    """
    Returns a list of sample borrowing transactions for users.
    """
    now = datetime.now()
    tx_list = [
        BorrowingTransaction(
            user_name="Alice Johnson",
            isbn="9781617294433",
            borrow_date=now - timedelta(days=5),
            period_days=14
        ),
        BorrowingTransaction(
            user_name="Bob Smith",
            isbn="10.48550/arXiv.1706.03762",
            borrow_date=now - timedelta(days=30),
            period_days=14
        ),
        BorrowingTransaction(
            user_name="Dr. Carol Lee",
            isbn="9780201616224",
            borrow_date=now - timedelta(days=15),
            period_days=14
        ),
        BorrowingTransaction(
            user_name="Guest User",
            isbn="9780451524935",
            borrow_date=now - timedelta(hours=1),
            period_days=7
        ),
        BorrowingTransaction(
            user_name="Librarian Lucy",
            isbn="9780261103344",
            borrow_date=now - timedelta(days=2),
            period_days=30
        )
    ]
   
    if tx_list[1].is_overdue():
        tx_list[1].status = TransactionStatus.OVERDUE
    # Carol returned
    tx_list[2].mark_returned(now)
    # Guest revoke within 2 hours
    try:
        tx_list[3].revoke()
    except Exception:
        pass
    # Lucy completed
    tx_list[4].complete_transaction()
    return tx_list


if __name__ == "__main__":
    print("Dummy Items:")
    for item in get_dummy_items(): print(item)

    print("\nDummy Users:")
    for user in get_dummy_users(): print(user)

    print("\nDummy Notifications:")
    for note in get_dummy_notifications(): print(note)

    print("\nDummy Reservations:")
    for res in get_dummy_reservations(): print(res)

    print("\nDummy Transactions:")
    for tx in get_dummy_transactions(): print(tx)