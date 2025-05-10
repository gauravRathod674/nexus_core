import sys
from models.users import Role
from models.items import ItemStatus, PrintedBook, EBook, Audiobook, ResearchPaper

from patterns.facade.library_facade import LibraryFacade
from patterns.factory.user_factory import LibraryUserFactory
from patterns.singleton.transaction_manager import TransactionManager
from patterns.observer.notification_center import NotificationCenter
from patterns.strategy.search_strategy import (
    SearchContext,
    KeywordSearchStrategy,
    AuthorSearchStrategy,
    TypeSearchStrategy,
    GenreSearchStrategy,
)
from additional_features.recommendation import (
    RecommendationEngine,
    HistoryBasedRecommendation,
    TrendingRecommendation,
)
from additional_features.dashboard import (
    check_availability,
    list_overdue,
    view_profile,
    manage_lending_policies,
    manage_user_roles,
    process_return,
)
from utils.dummy_data import get_dummy_items

# In‑memory stores
users_db = {}  # email -> LibraryUser
items_db = []  # list of LibraryItem


def seed_items():
    items_db.extend(get_dummy_items())

def seed_users():
    # ─── Register all roles with our Factory ─────────────────────────────
    LibraryUserFactory.register("student", Role.STUDENT)
    LibraryUserFactory.register("researcher", Role.RESEARCHER)
    LibraryUserFactory.register("faculty", Role.FACULTY)
    LibraryUserFactory.register("guest", Role.GUEST)
    LibraryUserFactory.register("librarian", Role.LIBRARIAN)


def show_start_menu():
    print("\n📚 Welcome to Nexus Library System")
    print("1) Register")
    print("2) Login")
    print("3) Exit")
    return input("Select an option: ").strip()


def register_user():
    print("\n--- Register New User ---")
    name  = input("Name: ").strip()
    email = input("Email: ").strip()
    if email in users_db:
        print("❌ That email is already registered.")
        return

    password = input("Password: ").strip()

    print("Select role:")
    for r in Role:
        print(f"  {r.value}) {r.name}")

    choice = input("Role number: ").strip()
    if not choice.isdigit():
        print("❌ Invalid input.")
        return

    try:
        role_enum = Role(int(choice))
    except ValueError:
        print("❌ Invalid role number.")
        return

    try:
        user = LibraryUserFactory.create(
            role_enum.name, name=name, email=email, password_hash=password
        )
    except ValueError as e:
        print(f"❌ {e}")
        return

    user.notifications = []
    users_db[email] = user
    print(f"✅ Registered {name} as {role_enum.name}.")

def login_user():
    print("\n--- Login ---")
    email = input("Email: ").strip()
    pwd   = input("Password: ").strip()

    user = users_db.get(email)
    if not user or user.password_hash != pwd:
        print("❌ Invalid credentials.")
        return None

    print(f"✅ Welcome back, {user.name} ({user.role.name})!")
    return user


def find_item_by_isbn(isbn: str):
    for it in items_db:
        if it.isbn == isbn:
            return it
    print("❌ ISBN not found.")
    return None


def search_books():
    # Strategy‐based search
    context = SearchContext(KeywordSearchStrategy())
    print("\nChoose search type:")
    print("  1) Keyword in title")
    print("  2) Author")
    print("  3) Item type")
    print("  4) Genre")
    choice = input("Enter choice [1-4]: ").strip()
    if choice == "1":
        context.set_strategy(KeywordSearchStrategy())
        prompt = "Enter keyword to search in titles: "
    elif choice == "2":
        context.set_strategy(AuthorSearchStrategy())
        prompt = "Enter author name to search: "
    elif choice == "3":
        context.set_strategy(TypeSearchStrategy())
        prompt = "Enter item type (e.g. E-Book, Printed Book): "
    elif choice == "4":
        context.set_strategy(GenreSearchStrategy())
        prompt = "Enter genre to search: "
    else:
        print("Invalid choice.")
        return

    q = input(prompt).strip()
    results = context.search(items_db, q)
    if not results:
        print("No matches.")
    else:
        print("Results:")
        for it in results:
            print(f"  {it.isbn} | {it.title} ({it.status.value})")


def view_book_details():
    if not items_db:
        print("No items in the catalog.")
        return

    print("\n📖 Full Catalog Details:")
    for it in items_db:
        print(f"\nISBN: {it.isbn}")
        print(f" Title           : {it.title}")
        print(f" Authors         : {', '.join(it.authors)}")
        print(f" Genres          : {', '.join(it.genres)}")
        print(f" Publication Year: {it.publication_year}")
        print(f" Language        : {it.language}")
        print(f" Status          : {it.status.value}")

        # Type‐specific fields
        if isinstance(it, PrintedBook):
            print(f" Shelf Location  : {it.shelf_location}")
        elif isinstance(it, EBook):
            print(f" File Format     : {it.file_format}")
        elif isinstance(it, Audiobook):
            print(f" Duration (mins) : {it.duration_minutes}")
        elif isinstance(it, ResearchPaper):
            print(f" Journal         : {it.journal}")

        print("-" * 50)

def show_borrow_history(user):
    tm = TransactionManager()
    user_tx = [tx for tx in tm.transactions if tx.user_name == user.name]
    if not user_tx:
        print("No borrowing history.")
        return
    print("Your Transactions:")
    for tx in user_tx:
        due = tx.due_date.strftime("%Y-%m-%d")
        print(f"  {tx.isbn} → {tx.status.name} (due {due})")


def view_notifications(user):
    if not getattr(user, "notifications", []):
        print("No notifications.")
        return
    print("Your Notifications:")
    for note in user.notifications:
        print("  🛈", note)
    user.notifications.clear()


def get_recommendations(user):
    tm = TransactionManager()
    txs = tm.transactions
    reservations = []
    for q in tm.reservation_queues.values():
        reservations.extend(q)

    engine = RecommendationEngine(HistoryBasedRecommendation(txs))
    recs = engine.recommend(user, items_db)
    if recs:
        print("\nBased on your borrowing history:")
        for it in recs:
            print(f"  • {it.title} ({it.isbn})")
    else:
        print("\nNo history‑based recommendations.")

    engine.set_strategy(TrendingRecommendation(txs, reservations))
    trending = engine.recommend(user, items_db)
    if trending:
        print("\nTrending items:")
        for it in trending:
            print(f"  • {it.title} ({it.isbn})")


def student_menu(user, facade: LibraryFacade):
    tm = TransactionManager()

    while True:
        print(f"\n📘 Student Menu ({user.name})")
        print("1) Search Books")
        print("2) View Book Details")
        print("3) Borrow a Book")
        print("4) Return a Book")
        print("5) Reserve a Book")
        print("6) View My Borrowing History")
        print("7) Undo Last Action")
        print("8) View Notifications")
        print("9) Get Recommendations")
        print("10) Check Book Availability")      
        print("11) List My Overdue Loans")   
        print("12) View My Profile")
        print("0) Logout")
        choice = input("Choice: ").strip()
        if choice == "0":
            break
        if choice == "1":
            search_books()
        elif choice == "2":
            view_book_details()
        elif choice == "3":
            it = find_item_by_isbn(input("ISBN to borrow: ").strip())
            if it:
                facade.borrow_book(user, it)
        elif choice == "4":
            it = find_item_by_isbn(input("ISBN to return: ").strip())
            if it:
                facade.return_book(user, it)
        elif choice == "5":
            it = find_item_by_isbn(input("ISBN to reserve: ").strip())
            if it:
                facade.reserve_book(user, it)
        elif choice == "6":
            show_borrow_history(user)
        elif choice == "7":
            facade.undo_last_action()
        elif choice == "8":
            view_notifications(user)
        elif choice == "9":
            get_recommendations(user)
        elif choice == "10":
            check_availability(items_db)
        elif choice == "11":
            list_overdue(user, tm.transactions)
        elif choice == "12":
            view_profile(user, items_db)
        else:
            print("Invalid choice.")


def researcher_menu(user, facade: LibraryFacade):
    tm = TransactionManager()

    while True:
        print(f"\n📗 Researcher Menu ({user.name})")
        print("1) Search Books")
        print("2) View Book Details")
        print("3) Borrow a Book")
        print("4) Return a Book")
        print("5) Reserve a Book")
        print("6) View My Borrowing History")
        print("7) Undo Last Action")
        print("8) View Notifications")
        print("9) Get Recommendations")
        print("10) Access Research Papers / Journals")
        print("11) Check Book Availability")      
        print("12) List My Overdue Loans")   
        print("13) View My Profile")
        print("0) Logout")
        choice = input("Choice: ").strip()
        if choice == "0":
            break
        if choice == "1":
            search_books()
        elif choice == "2":
            view_book_details()
        elif choice == "3":
            it = find_item_by_isbn(input("ISBN to borrow: ").strip())
            if it:
                facade.borrow_book(user, it)
        elif choice == "4":
            it = find_item_by_isbn(input("ISBN to return: ").strip())
            if it:
                facade.return_book(user, it)
        elif choice == "5":
            it = find_item_by_isbn(input("ISBN to reserve: ").strip())
            if it:
                facade.reserve_book(user, it)
        elif choice == "6":
            show_borrow_history(user)
        elif choice == "7":
            facade.undo_last_action()
        elif choice == "8":
            view_notifications(user)
        elif choice == "9":
            get_recommendations(user)
        elif choice == "10":
            print("\nAvailable Research Papers:")
            for it in items_db:
                if it.item_type() == "Research Paper":
                    print(f"  {it.isbn} | {it.title}")
        elif choice == "11":
            check_availability(items_db)
        elif choice == "12":
            list_overdue(user, tm.transactions)
        elif choice == "13":
            view_profile(user, items_db)
        else:
            print("Invalid choice.")


def faculty_menu(user, facade: LibraryFacade):
    tm = TransactionManager()

    while True:
        print(f"\n📙 Faculty Menu ({user.name})")
        print("1) Search Books")
        print("2) View Book Details")
        print("3) Borrow a Book")
        print("4) Return a Book")
        print("5) Reserve a Book")
        print("6) View My Borrowing History")
        print("7) Undo Last Action")
        print("8) View Notifications")
        print("9) Get Recommendations")
        print("10) Access Research Papers / Journals")
        print("11) Request Custom Book Addition")
        print("12) Check Book Availability")       # <-- new
        print("13) List My Overdue Loans")         # <-- new
        print("14) View My Profile")
        print("0) Logout")
        choice = input("Choice: ").strip()
        if choice == "0":
            break
        if choice == "1":
            search_books()
        elif choice == "2":
            view_book_details()
        elif choice == "3":
            it = find_item_by_isbn(input("ISBN to borrow: ").strip())
            if it:
                facade.borrow_book(user, it)
        elif choice == "4":
            it = find_item_by_isbn(input("ISBN to return: ").strip())
            if it:
                facade.return_book(user, it)
        elif choice == "5":
            it = find_item_by_isbn(input("ISBN to reserve: ").strip())
            if it:
                facade.reserve_book(user, it)
        elif choice == "6":
            show_borrow_history(user)
        elif choice == "7":
            facade.undo_last_action()
        elif choice == "8":
            view_notifications(user)
        elif choice == "9":
            get_recommendations(user)
        elif choice == "10":
            print("\nAvailable Research Papers:")
            for it in items_db:
                if it.item_type() == "Research Paper":
                    print(f"  {it.isbn} | {it.title}")
        elif choice == "11":
            title = input("Custom book title: ").strip()
            isbn = input("ISBN: ").strip()
            new_book = PrintedBook(
                title=title,
                authors=["(pending)"],
                isbn=isbn,
                genres=["Custom"],
                publication_year=2025,
                language="English",
                status=ItemStatus.AVAILABLE,
                shelf_location="TBD",
            )
            items_db.append(new_book)
            print(f"Requested '{title}' for addition.")
        elif choice == "12":
            check_availability(items_db)
        elif choice == "13":
            list_overdue(user, tm.transactions)
        elif choice == "14":
            view_profile(user, items_db)
        else:
            print("Invalid choice.")


def guest_menu(user):
    while True:
        print(f"\n📕 Guest Menu ({user.name})")
        print("1) Search Books")
        print("2) View Book Details")
        print("0) Logout")
        choice = input("Choice: ").strip()
        if choice == "0":
            break
        if choice == "1":
            search_books()
        elif choice == "2":
            view_book_details()
        else:
            print("Invalid choice.")


def librarian_menu(user, facade: LibraryFacade):
    tm = TransactionManager()
    all_users = list(users_db.values())

    while True:
        print(f"\n🖥 Librarian Menu ({user.name})")
        print("1) Search Books")
        print("2) View Book Details")
        print("3) Borrow a Book")
        print("4) Return a Book")
        print("5) Reserve a Book")
        print("6) View All Borrowing Records")
        print("7) Undo Any Action")
        print("8) View Notifications")
        print("9) Get Recommendations")
        print("10) Check Book Availability")
        print("11) List Overdue Loans")
        print("12) View Profile")
        print("13) Manage Lending Policies")
        print("14) Manage User Roles")
        print("15) Process a Return")
        print("0) Logout")
        choice = input("Choice: ").strip()
        if choice == "0":
            break
        if choice == "1":
            search_books()
        elif choice == "2":
            view_book_details()
        elif choice == "3":
            it = find_item_by_isbn(input("ISBN to borrow: ").strip())
            if it:
                facade.borrow_book(user, it)
        elif choice == "4":
            it = find_item_by_isbn(input("ISBN to return: ").strip())
            if it:
                facade.return_book(user, it)
        elif choice == "5":
            it = find_item_by_isbn(input("ISBN to reserve: ").strip())
            if it:
                facade.reserve_book(user, it)
        elif choice == "6":
            tm = TransactionManager()
            print("\nAll Transactions:")
            for tx in tm.transactions:
                print(f"  {tx}")
        elif choice == "7":
            facade.undo_last_action()
        elif choice == "8":
            # Notify via subject to demonstrate observer
            NotificationCenter.get_subject().notify(
                "due_date_approaching",
                user=user,
                item=items_db[0],
                due_date="2025-05-15",
            )
        elif choice == "9":
            get_recommendations(user)
        elif choice == "10":
            check_availability(items_db)
        elif choice == "11":
            list_overdue(user, tm.transactions)
        elif choice == "12":
            view_profile(user, items_db)
        elif choice == "13":
            manage_lending_policies()
        elif choice == "14":
            manage_user_roles(all_users)
        elif choice == "15":
            process_return(tm, all_users, items_db)
        else:
            print("Invalid choice.")


def main_menu(user):
    facade = LibraryFacade()
    if user.role == Role.STUDENT:
        student_menu(user, facade)
    elif user.role == Role.RESEARCHER:
        researcher_menu(user, facade)
    elif user.role == Role.FACULTY:
        faculty_menu(user, facade)
    elif user.role == Role.GUEST:
        guest_menu(user)
    elif user.role == Role.LIBRARIAN:
        librarian_menu(user, facade)


def main():
    seed_users()
    seed_items()
    while True:
        choice = show_start_menu()
        if choice == "1":
            register_user()
        elif choice == "2":
            user = login_user()
            if user:
                main_menu(user)
        elif choice == "3":
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
