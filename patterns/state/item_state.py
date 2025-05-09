from abc import ABC, abstractmethod
from models.items import ItemStatus  


class ItemState(ABC):
    @abstractmethod
    def borrow(self, item, user): pass

    @abstractmethod
    def return_item(self, item, user): pass

    @abstractmethod
    def reserve(self, item, user): pass


class AvailableState(ItemState):
    def borrow(self, item, user):
        from patterns.singleton.transaction_manager import TransactionManager
        from patterns.state.item_state import CheckedOutState

        ok, msg = TransactionManager().borrow_item(user, item)
        if ok:
            item.update_status(ItemStatus.CHECKED_OUT)
            item._state = CheckedOutState()
        return ok, msg

    def return_item(self, item, user):
        return False, "Item is already available."

    def reserve(self, item, user):
        from patterns.singleton.transaction_manager import TransactionManager
        from patterns.state.item_state import ReservedState

        ok, msg = TransactionManager().reserve_item(user, item)
        if ok:
            item.update_status(ItemStatus.RESERVED)
            item._state = ReservedState()
        return ok, msg


class CheckedOutState(ItemState):
    def borrow(self, item, user):
        return False, "Item is already checked out."

    def return_item(self, item, user):
        from patterns.singleton.transaction_manager import TransactionManager
        from patterns.state.item_state import ReservedState, AvailableState

        ok, msg = TransactionManager().return_item(user, item)
        if ok:
            # If someone’s on the reservation queue → RESERVED  
            if TransactionManager()._get_first_active_reservation(item.isbn):
                item.update_status(ItemStatus.RESERVED)
                item._state = ReservedState()
            else:
                item.update_status(ItemStatus.AVAILABLE)
                item._state = AvailableState()
        return ok, msg

    def reserve(self, item, user):
        from patterns.singleton.transaction_manager import TransactionManager
        return TransactionManager().reserve_item(user, item)


class ReservedState(ItemState):
    def borrow(self, item, user):
        from patterns.singleton.transaction_manager import TransactionManager
        from patterns.state.item_state import CheckedOutState

        ok, msg = TransactionManager().borrow_item(user, item)
        if ok:
            item.update_status(ItemStatus.CHECKED_OUT)
            item._state = CheckedOutState()
        return ok, msg

    def return_item(self, item, user):
        return False, "Cannot return a reserved item unless it’s been borrowed."

    def reserve(self, item, user):
        return False, "Item is already reserved."


class UnderReviewState(ItemState):
    def borrow(self, item, user):
        return False, "Item is under review and unavailable."

    def return_item(self, item, user):
        return False, "Item is under review."

    def reserve(self, item, user):
        return False, "Item is under review."


# ──── Self‑test main() ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    from patterns.singleton.transaction_manager import TransactionManager
    from models.users import LibraryUser, Role
    from models.items import PrintedBook, EBook, Audiobook, ResearchPaper, ItemStatus
    from patterns.state.item_state import UnderReviewState

    # 1) Reset singleton storage for a clean run:
    tm = TransactionManager()
    tm.transactions.clear()
    tm.reservation_queues.clear()

    # 2) Verify Singleton
    print("TransactionManager Singleton works? ", tm is TransactionManager())

    # 3) Create users & items
    alice   = LibraryUser("alice",   "a@x", "h", Role.STUDENT)
    bob     = LibraryUser("bob",     "b@x", "h", Role.RESEARCHER)
    guest   = LibraryUser("guest",   "g@x", "h", Role.GUEST)

    book    = PrintedBook(
        title="1984",
        authors=["Orwell"],
        isbn="ISBN0001",
        genres=["Dystopia"],
        publication_year=1949,
        language="English",
        status=ItemStatus.AVAILABLE,
        shelf_location="A1"
    )

    # Helper to print outcome
    def out(action, user, item=None):
        if item:
            ok, msg = action(item, user)
            print(f"{action.__name__:<15} | {item.status.name:<12} | {user.role.name:<9} → "
                  f"{'✔' if ok else '✘'} {msg}")
        else:
            ok, msg = action(user)
            print(f"{action.__name__:<15} | {'-':<12} | {user.role.name:<9} → "
                  f"{'✔' if ok else '✘'} {msg}")

    print("\n-- Borrow Available --")
    out(PrintedBook.borrow, alice, book)

    print("\n-- Borrow Already Checked Out --")
    out(PrintedBook.borrow, alice, book)

    print("\n-- Return Checked Out --")
    out(PrintedBook.return_item, alice, book)

    print("\n-- Return Already Available --")
    out(PrintedBook.return_item, alice, book)

    print("\n-- Reserve Available --")
    out(PrintedBook.reserve, alice, book)

    print("\n-- Reserve Already Reserved --")
    out(PrintedBook.reserve, bob, book)

    print("\n-- Borrow Reserved by Alice --")
    out(PrintedBook.borrow, alice, book)

    print("\n-- Under Review Behavior --")
    # force into under_review
    book.status = ItemStatus.UNDER_REVIEW
    book._state = UnderReviewState()
    out(PrintedBook.borrow, alice, book)
    out(PrintedBook.reserve, alice, book)
    out(PrintedBook.return_item, alice, book)
