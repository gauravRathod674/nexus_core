from models.users import LibraryUser, Role
from models.items import *
from .singleton import Singleton
from typing import Tuple


class AccessControlManager(Singleton):
    """
    Singleton for all role-based permission checks in Nexus Library.
    """

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

    def can_borrow(self, user: LibraryUser, item: LibraryItem):
        if user.role == Role.GUEST:
            return False, "Guests cannot borrow items."

        if item.item_type() == "Research Paper" and user.role not in (Role.FACULTY, Role.RESEARCHER):
            return False, "Only Faculty or Researchers may borrow research papers."

        if len(user.current_loans) >= user.get_borrow_limit():
            limit = user.get_borrow_limit()
            return False, f"Borrow limit reached ({limit} items)."

        return True, ""

    def can_reserve(self, user: LibraryUser, item: LibraryItem):
        if user.role == Role.GUEST:
            return False, "Guests cannot place reservations."

        if item.item_type() == "Research Paper" and user.role not in (Role.FACULTY, Role.RESEARCHER):
            return False, "Only Faculty or Researchers may reserve research papers."

        return True, ""

    def can_download(self, user: LibraryUser, item: LibraryItem):
        digital_kinds = {"E-Book", "Audiobook"}
        if item.item_type() not in digital_kinds:
            return False, "This item is not available for download."
        if user.role == Role.GUEST:
            return False, "Guests cannot download digital content."
        return True, ""

    def can_request_paper(self, user: LibraryUser):
        """
        Restricted digital collections (e.g., archives, research papers).
        """
        if user.role in (Role.FACULTY, Role.RESEARCHER, Role.LIBRARIAN):
            return True, ""
        return False, "Only Faculty, Researchers, and Librarians may request research papers."

    def can_edit_catalog(self, user: LibraryUser):
        if user.role == Role.LIBRARIAN:
            return True, ""
        return False, "Only Librarians may edit the catalog."


def main():
    # Verify Singleton behavior
    acm1 = AccessControlManager()
    acm2 = AccessControlManager()
    print("Singleton test: acm1 is acm2 ->", acm1 is acm2)

    # Sample users
    users = [
        LibraryUser("Alice", "alice@uni.edu", "hash", Role.STUDENT),
        LibraryUser("Bob",   "bob@uni.edu",   "hash", Role.RESEARCHER),
        LibraryUser("Carol", "carol@uni.edu", "hash", Role.FACULTY),
        LibraryUser("Dave",  "dave@uni.edu",  "hash", Role.GUEST),
        LibraryUser("Erin",  "erin@uni.edu",  "hash", Role.LIBRARIAN),
    ]

    # Sample items
    items = [
        EBook("E-Python",    ["X. Author"], "EBK001", ["Tech"], 2021, "English", ItemStatus.AVAILABLE, file_format="PDF"),
        PrintedBook("C++ 101",["Y. Author"], "PBK002", ["Tech"], 2019, "English", ItemStatus.AVAILABLE, shelf_location="A1"),
        Audiobook("Java Pro",["Z. Author"], "ABK003", ["Tech"], 2020, "English", ItemStatus.AVAILABLE, duration_minutes=300),
        ResearchPaper("Quantum AI", ["Q. Sci"], "RP004", ["Science"], 2022, "English", ItemStatus.AVAILABLE, journal="SciToday"),
    ]

    def check(method, user, item=None):
        if item:
            allowed, reason = method(user, item)
            icon = "✔" if allowed else "✘"
            print(f"{user.role.name:<10} {item.item_type():<15} → {icon} {reason}")
        else:
            allowed, reason = method(user)
            icon = "✔" if allowed else "✘"
            print(f"{user.role.name:<10}            → {icon} {reason}")

    print("\n--- can_borrow ---")
    for u in users:
        for it in items:
            check(acm1.can_borrow, u, it)

    print("\n--- can_reserve ---")
    for u in users:
        for it in items:
            check(acm1.can_reserve, u, it)

    print("\n--- can_download ---")
    for u in users:
        for it in items:
            check(acm1.can_download, u, it)

    print("\n--- can_request_paper ---")
    for u in users:
        check(acm1.can_request_paper, u)

    print("\n--- can_edit_catalog ---")
    for u in users:
        check(acm1.can_edit_catalog, u)


if __name__ == "__main__":
    main()