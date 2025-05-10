from datetime import datetime, timedelta
from models.items import EBook, PrintedBook, ResearchPaper, Audiobook, ItemStatus
from models.users import LibraryUser, Role
from models.notification import Notification
from models.reservation import Reservation
from models.transactions import BorrowingTransaction, TransactionStatus
from patterns.factory.item_factory import LibraryItemFactory

def get_dummy_items():
    """ Returns a list of dummy library items covering all types, built via our Factory. """

    LibraryItemFactory.register("ebook", EBook)
    LibraryItemFactory.register("printedbook", PrintedBook)
    LibraryItemFactory.register("researchpaper", ResearchPaper)
    LibraryItemFactory.register("audiobook", Audiobook)

    return [
        LibraryItemFactory.create(
            "ebook",
            title="Deep Learning with Python",
            authors=["Francois Chollet"],
            isbn="9781617294433",
            genres=["AI", "Deep Learning"],
            publication_year=2017,
            language="English",
            status=ItemStatus.AVAILABLE,
            file_format="PDF",
        ),
        LibraryItemFactory.create(
            "ebook",
            title="Automate the Boring Stuff",
            authors=["Al Sweigart"],
            isbn="9781593275990",
            genres=["Programming", "Python"],
            publication_year=2019,
            language="English",
            status=ItemStatus.AVAILABLE,
            file_format="ePub",
        ),
        LibraryItemFactory.create(
            "printedbook",
            title="Clean Code",
            authors=["Robert C. Martin"],
            isbn="9780132350884",
            genres=["Software Engineering"],
            publication_year=2008,
            language="English",
            status=ItemStatus.AVAILABLE,
            shelf_location="A3-42",
        ),
        LibraryItemFactory.create(
            "printedbook",
            title="The Pragmatic Programmer",
            authors=["Andrew Hunt", "David Thomas"],
            isbn="9780201616224",
            genres=["Software Engineering"],
            publication_year=1999,
            language="English",
            status=ItemStatus.AVAILABLE,
            shelf_location="B1-15",
        ),
        LibraryItemFactory.create(
            "researchpaper",
            title="Attention Is All You Need",
            authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
            isbn="10.48550/arXiv.1706.03762",
            genres=["AI", "NLP"],
            publication_year=2017,
            language="English",
            status=ItemStatus.AVAILABLE,
            journal="NeurIPS",
        ),
        LibraryItemFactory.create(
            "researchpaper",
            title="ImageNet Classification with Deep Convolutional Neural Networks",
            authors=["Alex Krizhevsky", "Ilya Sutskever", "Geoffrey E. Hinton"],
            isbn="10.1145/3065386",
            genres=["AI", "Computer Vision"],
            publication_year=2012,
            language="English",
            status=ItemStatus.AVAILABLE,
            journal="NIPS",
        ),
        LibraryItemFactory.create(
            "audiobook",
            title="The Hobbit",
            authors=["J.R.R. Tolkien"],
            isbn="9780261103344",
            genres=["Fantasy", "Adventure"],
            publication_year=1937,
            language="English",
            status=ItemStatus.AVAILABLE,
            duration_minutes=720,
        ),
        LibraryItemFactory.create(
            "audiobook",
            title="1984",
            authors=["George Orwell"],
            isbn="9780451524935",
            genres=["Dystopian", "Political Fiction"],
            publication_year=1949,
            language="English",
            status=ItemStatus.AVAILABLE,
            duration_minutes=650,
        ),
    ]

DUMMY_USERS = [
    LibraryUser("Gaurav Rathod",   "gaurav@example.com",   "hash1", Role.STUDENT),
    LibraryUser("Mohsin Pathan",   "mohsin@example.com",   "hash2", Role.RESEARCHER),
    LibraryUser("Chandresh Thakkar","chandresh@example.edu","hash3", Role.FACULTY),
    LibraryUser("Nitesh Sachde",   "nitesh@example.com",   "hash4", Role.GUEST),
    LibraryUser("Sourish Dasgupta","sourish@example.com", "hash5", Role.LIBRARIAN),
]

def get_dummy_users():
    return DUMMY_USERS

def get_dummy_notifications():
    """ Returns a list of sample notifications for users. """
    now = datetime.now()
    return [
        Notification(
            user_name="Gaurav Rathod",
            message="Your loan for 'Deep Learning with Python' is due in 3 days.",
            timestamp=now - timedelta(days=1)
        ),
        Notification(
            user_name="Mohsin Pathan",
            message="The item 'Attention Is All You Need' is now available for pickup.",
            timestamp=now - timedelta(hours=2)
        ),
        Notification(
            user_name="Chandresh Thakkar",
            message="Your reservation for 'The Pragmatic Programmer' is confirmed.",
            timestamp=now - timedelta(minutes=30)
        ),
        Notification(
            user_name="Nitesh Sachde",
            message="As a guest, you cannot borrow items. Please register for full access.",
            timestamp=now - timedelta(days=2, hours=5)
        ),
        Notification(
            user_name="Sourish Dasgupta",
            message="System maintenance scheduled for tomorrow at 2 AM.",
            timestamp=now
        )
    ]

def get_dummy_reservations():
    """ Returns a list of sample reservations for users. """
    now = datetime.now()
    res_list = [
        Reservation(
            user_name="Gaurav Rathod",
            isbn="9780132350884",
            reservation_date=now - timedelta(days=1)
        ),
        Reservation(
            user_name="Mohsin Pathan",
            isbn="10.48550/arXiv.1706.03762",
            reservation_date=now - timedelta(days=3)
        ),
        Reservation(
            user_name="Chandresh Thakkar",
            isbn="9780201616224",
            reservation_date=now
        ),
        Reservation(
            user_name="Nitesh Sachde",
            isbn="9780451524935",
            reservation_date=now - timedelta(hours=5)
        ),
        Reservation(
            user_name="Sourish Dasgupta",
            isbn="9780261103344",
            reservation_date=now - timedelta(days=2)
        )
    ]
    # expire/cancel some
    for res in res_list:
        if res.user_name == "Mohsin Pathan":
            res.expire()
        if res.user_name == "Sourish Dasgupta":
            res.cancel()
    return res_list

def get_dummy_transactions():
    """ Returns a list of sample borrowing transactions for users. """
    now = datetime.now()
    tx_list = [
        BorrowingTransaction(
            user_name="Gaurav Rathod",
            isbn="9781617294433",
            borrow_date=now - timedelta(days=5),
            period_days=14
        ),
        BorrowingTransaction(
            user_name="Mohsin Pathan",
            isbn="10.48550/arXiv.1706.03762",
            borrow_date=now - timedelta(days=30),
            period_days=14
        ),
        BorrowingTransaction(
            user_name="Chandresh Thakkar",
            isbn="9780201616224",
            borrow_date=now - timedelta(days=15),
            period_days=14
        ),
        BorrowingTransaction(
            user_name="Nitesh Sachde",
            isbn="9780451524935",
            borrow_date=now - timedelta(hours=1),
            period_days=7
        ),
        BorrowingTransaction(
            user_name="Sourish Dasgupta",
            isbn="9780261103344",
            borrow_date=now - timedelta(days=2),
            period_days=30
        )
    ]
    if tx_list[1].is_overdue():
        tx_list[1].status = TransactionStatus.OVERDUE
    # Chandresh returned
    tx_list[2].mark_returned(now)
    # Nitesh revoke within 2 hours
    try:
        tx_list[3].revoke()
    except Exception:
        pass
    # Sourish completed
    tx_list[4].complete_transaction()
    return tx_list

if __name__ == "__main__":
    print("Dummy Items:")
    for item in get_dummy_items():
        print(item)
    print("\nDummy Users:")
    for user in get_dummy_users():
        print(user)
    print("\nDummy Notifications:")
    for note in get_dummy_notifications():
        print(note)
    print("\nDummy Reservations:")
    for res in get_dummy_reservations():
        print(res)
    print("\nDummy Transactions:")
    for tx in get_dummy_transactions():
        print(tx)
