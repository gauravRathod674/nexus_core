import sys
from datetime import datetime

from models.users import Role
from models.items import ItemStatus, PrintedBook, EBook, Audiobook, ResearchPaper
from patterns.facade.library_facade import LibraryFacade
from patterns.factory.user_factory import LibraryUserFactory
from patterns.singleton.transaction_manager import TransactionManager
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
from additional_features.dashboard import Dashboard
from utils.dummy_data import get_dummy_items

class NexusLibraryApp:
    def __init__(self):
        self.users_db = {}      # email -> LibraryUser
        self.items_db = []      # list of LibraryItem
        self.tm = TransactionManager()
        self.facade = LibraryFacade()
        self.dashboard = Dashboard(self.users_db, self.items_db, self.tm)
        self._seed_users()
        self._seed_items()

    def _seed_users(self):
        LibraryUserFactory.register("student", Role.STUDENT)
        LibraryUserFactory.register("researcher", Role.RESEARCHER)
        LibraryUserFactory.register("faculty", Role.FACULTY)
        LibraryUserFactory.register("guest", Role.GUEST)
        LibraryUserFactory.register("librarian", Role.LIBRARIAN)

    def _seed_items(self):
        self.items_db.extend(get_dummy_items())

    def run(self):
        while True:
            choice = self._show_start_menu()
            if choice == "1":
                self._register_user()
            elif choice == "2":
                user = self._login_user()
                if user:
                    self._main_menu(user)
            elif choice == "3":
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("Invalid choice.")

    def _show_start_menu(self) -> str:
        print("\n📚 Welcome to Nexus Library System")
        print("1) Register")
        print("2) Login")
        print("3) Exit")
        return input("Select an option: ").strip()

    def _register_user(self):
        print("\n--- Register New User ---")
        name = input("Name: ").strip()
        email = input("Email: ").strip()
        if email in self.users_db:
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
        self.users_db[email] = user
        print(f"✅ Registered {name} as {role_enum.name}.")

    def _login_user(self):
        print("\n--- Login ---")
        email = input("Email: ").strip()
        pwd = input("Password: ").strip()
        user = self.users_db.get(email)
        if not user or user.password_hash != pwd:
            print("❌ Invalid credentials.")
            return None
        print(f"✅ Welcome back, {user.name} ({user.role.name})!")
        return user

    def _main_menu(self, user):
        role = user.role
        if role == Role.STUDENT:
            self._student_menu(user)
        elif role == Role.RESEARCHER:
            self._researcher_menu(user)
        elif role == Role.FACULTY:
            self._faculty_menu(user)
        elif role == Role.GUEST:
            self._guest_menu(user)
        elif role == Role.LIBRARIAN:
            self._librarian_menu(user)

    def _find_item(self, prompt: str = "Enter ISBN: "):
        isbn = input(prompt).strip()
        item = next((it for it in self.items_db if it.isbn == isbn), None)
        if not item:
            print("❌ ISBN not found.")
        return item

    def _search_books(self):
        context = SearchContext(KeywordSearchStrategy())
        print("\nChoose search type:")
        print("  1) Keyword in title")
        print("  2) Author")
        print("  3) Item type")
        print("  4) Genre")
        choice = input("Enter choice [1-4]: ").strip()
        strategies = {
            "1": (KeywordSearchStrategy, "Enter keyword to search in titles: "),
            "2": (AuthorSearchStrategy,  "Enter author name to search: " ),
            "3": (TypeSearchStrategy,    "Enter item type (e.g. E-Book, Printed Book): " ),
            "4": (GenreSearchStrategy,   "Enter genre to search: " ),
        }
        strat_class, prompt = strategies.get(choice, (None, None))
        if not strat_class:
            print("Invalid choice.")
            return
        context.set_strategy(strat_class())
        q = input(prompt).strip()
        results = context.search(self.items_db, q)
        if not results:
            print("No matches.")
        else:
            print("Results:")
            for it in results:
                print(f"  {it.isbn} | {it.title} ({it.status.value})")

    def _view_book_details(self):
        if not self.items_db:
            print("No items in the catalog.")
            return
        print("\n📖 Full Catalog Details:")
        for it in self.items_db:
            print(f"\nISBN: {it.isbn}")
            print(f" Title           : {it.title}")
            print(f" Authors         : {', '.join(it.authors)}")
            print(f" Genres          : {', '.join(it.genres)}")
            print(f" Publication Year: {it.publication_year}")
            print(f" Language        : {it.language}")
            print(f" Status          : {it.status.value}")
            if isinstance(it, PrintedBook):
                print(f" Shelf Location  : {it.shelf_location}")
            elif isinstance(it, EBook):
                print(f" File Format     : {it.file_format}")
            elif isinstance(it, Audiobook):
                print(f" Duration (mins) : {it.duration_minutes}")
            elif isinstance(it, ResearchPaper):
                print(f" Journal         : {it.journal}")
            print("-" * 50)

    def _show_history(self, user):
        txs = [tx for tx in self.tm.transactions if tx.user_name == user.name]
        if not txs:
            print("No borrowing history.")
            return
        print("Your Transactions:")
        for tx in txs:
            print(f"  {tx.isbn} → {tx.status.name} (due {tx.due_date.date()})")

    def _view_notifications(self, user):
        notes = getattr(user, "notifications", [])
        if not notes:
            print("No notifications.")
            return
        print("Your Notifications:")
        for note in notes:
            print(f"  🛈 {note}")
        user.notifications.clear()

    def _get_recommendations(self, user):
        engine = RecommendationEngine(HistoryBasedRecommendation(self.tm.transactions))
        recs = engine.recommend(user, self.items_db)
        if recs:
            print("\nBased on your borrowing history:")
            for it in recs:
                print(f"  • {it.title} ({it.isbn})")
        engine.set_strategy(TrendingRecommendation(
            self.tm.transactions,
            [u for q in self.tm.reservation_queues.values() for u in q]
        ))
        trending = engine.recommend(user, self.items_db)
        if trending:
            print("\nTrending items:")
            for it in trending:
                print(f"  • {it.title} ({it.isbn})")

    def _student_menu(self, user):
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
            if choice == "0": break
            if choice == "1": self._search_books()
            elif choice == "2": self._view_book_details()
            elif choice == "3":
                item = self._find_item("ISBN to borrow: ")
                if item: self.facade.borrow_book(user, item)
            elif choice == "4":
                item = self._find_item("ISBN to return: ")
                if item: self.facade.return_book(user, item)
            elif choice == "5":
                item = self._find_item("ISBN to reserve: ")
                if item: self.facade.reserve_book(user, item)
            elif choice == "6": self._show_history(user)
            elif choice == "7": self.facade.undo_last_action()
            elif choice == "8": self._view_notifications(user)
            elif choice == "9": self._get_recommendations(user)
            elif choice == "10": self.dashboard.check_availability()
            elif choice == "11": self.dashboard.list_overdue(user)
            elif choice == "12": self.dashboard.view_profile(user)
            else: print("Invalid choice.")

    def _researcher_menu(self, user):
        while True:
            print(f"\n🔬 Researcher Menu ({user.name})")
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
            if choice == "0": break
            if choice == "1": self._search_books()
            elif choice == "2": self._view_book_details()
            elif choice == "3":
                item = self._find_item("ISBN to borrow: ")
                if item: self.facade.borrow_book(user, item)
            elif choice == "4":
                item = self._find_item("ISBN to return: ")
                if item: self.facade.return_book(user, item)
            elif choice == "5":
                item = self._find_item("ISBN to reserve: ")
                if item: self.facade.reserve_book(user, item)
            elif choice == "6": self._show_history(user)
            elif choice == "7": self.facade.undo_last_action()
            elif choice == "8": self._view_notifications(user)
            elif choice == "9": self._get_recommendations(user)
            elif choice == "10":
                print("\nAvailable Research Papers:")
                for it in self.items_db:
                    if isinstance(it, ResearchPaper):
                        print(f"  {it.isbn} | {it.title}")
            elif choice == "11": self.dashboard.check_availability()
            elif choice == "12": self.dashboard.list_overdue(user)
            elif choice == "13": self.dashboard.view_profile(user)
            else: print("Invalid choice.")

    def _faculty_menu(self, user):
        while True:
            print(f"\n🎓 Faculty Menu ({user.name})")
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
            print("12) Check Book Availability")
            print("13) List My Overdue Loans")
            print("14) View My Profile")
            print("0) Logout")
            choice = input("Choice: ").strip()
            if choice == "0": break
            if choice == "1": self._search_books()
            elif choice == "2": self._view_book_details()
            elif choice == "3":
                item = self._find_item("ISBN to borrow: ")
                if item: self.facade.borrow_book(user, item)
            elif choice == "4":
                item = self._find_item("ISBN to return: ")
                if item: self.facade.return_book(user, item)
            elif choice == "5":
                item = self._find_item("ISBN to reserve: ")
                if item: self.facade.reserve_book(user, item)
            elif choice == "6": self._show_history(user)
            elif choice == "7": self.facade.undo_last_action()
            elif choice == "8": self._view_notifications(user)
            elif choice == "9": self._get_recommendations(user)
            elif choice == "10":
                print("\nAvailable Research Papers:")
                for it in self.items_db:
                    if isinstance(it, ResearchPaper):
                        print(f"  {it.isbn} | {it.title}")
            elif choice == "11":
                title = input("Custom book title: ").strip()
                isbn = input("ISBN: ").strip()
                new_book = PrintedBook(
                    title=title,
                    authors=["(pending)"],
                    isbn=isbn,
                    genres=["Custom"],
                    publication_year=datetime.now().year,
                    language="English",
                    status=ItemStatus.AVAILABLE,
                    shelf_location="TBD",
                )
                self.items_db.append(new_book)
                print(f"Requested '{title}' for addition.")
            elif choice == "12": self.dashboard.check_availability()
            elif choice == "13": self.dashboard.list_overdue(user)
            elif choice == "14": self.dashboard.view_profile(user)
            else: print("Invalid choice.")

    def _guest_menu(self, user):
        while True:
            print(f"\n🎟️ Guest Menu ({user.name})")
            print("1) Search Books")
            print("2) View Book Details")
            print("0) Logout")
            choice = input("Choice: ").strip()
            if choice == "0": break
            if choice == "1": self._search_books()
            elif choice == "2": self._view_book_details()
            else: print("Invalid choice.")

    def _librarian_menu(self, user):
        all_users = list(self.users_db.values())
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
            if choice == "0": break
            if choice == "1": self._search_books()
            elif choice == "2": self._view_book_details()
            elif choice == "3":
                item = self._find_item("ISBN to borrow: ")
                if item: self.facade.borrow_book(user, item)
            elif choice == "4":
                item = self._find_item("ISBN to return: ")
                if item: self.facade.return_book(user, item)
            elif choice == "5":
                item = self._find_item("ISBN to reserve: ")
                if item: self.facade.reserve_book(user, item)
            elif choice == "6":
                print("\nAll Transactions:")
                for tx in self.tm.transactions:
                    print(f"  {tx}")
            elif choice == "7": self.facade.undo_last_action()
            elif choice == "8": self._view_notifications(user)
            elif choice == "9": self._get_recommendations(user)
            elif choice == "10": self.dashboard.check_availability()
            elif choice == "11": self.dashboard.list_overdue(user)
            elif choice == "12": self.dashboard.view_profile(user)
            elif choice == "13": self.dashboard.manage_lending_policies()
            elif choice == "14": self.dashboard.manage_user_roles()
            elif choice == "15": self.dashboard.process_return()
            else: print("Invalid choice.")

if __name__ == "__main__":
    app = NexusLibraryApp()
    app.run()
