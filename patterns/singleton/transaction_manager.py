from datetime import datetime, timedelta
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.items import LibraryItem

from models.users import LibraryUser, Role
from models.items import LibraryItem, ItemStatus, PrintedBook
from models.transactions import BorrowingTransaction, TransactionStatus
from models.reservation import Reservation, ReservationStatus
from .singleton import Singleton
from patterns.observer.notification_center import NotificationCenter


class TransactionManager(Singleton):
    """
    Manages:
      • Borrowing
      • Returning
      • Revoking (undo borrow within 2 hours)
      • Reserving (FIFO queue + 2-day pickup window)
    """

    def __init__(self):
        # only initialize once in this singleton
        if hasattr(self, "_initialized"):
            return

        self.transactions = []  # list of BorrowingTransaction
        self.reservation_queues = {}  # isbn -> list of Reservation
        self._initialized = True    

    # ─── Borrow ────────────────────────────────────────────────────────────────
    def borrow_item(self,  user: "LibraryUser", item: "LibraryItem"):
        # 1) If book is RESERVED, only the first active reserver can borrow
        queue = self.reservation_queues.get(item.isbn, [])
        first_hold = self._get_first_active_reservation(item.isbn)

        if item.status == ItemStatus.RESERVED:
            if not first_hold or first_hold.user_name != user.name:
                holder = first_hold.user_name if first_hold else "another user"
                return False, f"Item is reserved for {holder}."
            # consume this reservation
            queue.pop(0)
            item.update_status(ItemStatus.AVAILABLE)

        # 2) Permission and availability checks
        if not user.can_borrow(item.item_type()):
            return False, "You do not have permission to borrow this item."

        if item.status != ItemStatus.AVAILABLE:
            return False, f"Item is currently {item.status.value}."

        # 3) Create transaction
        days_allowed = user.get_borrow_duration()
        tx = BorrowingTransaction(
            user_name=user.name,
            isbn=item.isbn,
            borrow_date=datetime.now(),
            period_days=days_allowed,
        )
        self.transactions.append(tx)

        # 4) Update user and item
        user.current_loans.append(item.isbn)
        item.update_status(ItemStatus.CHECKED_OUT)

        return True, f"Successfully borrowed '{item.title}'."

    # ─── Return ────────────────────────────────────────────────────────────────
    def return_item(self, user: LibraryUser, item: LibraryItem):
        tx = self._find_active_transaction(user.name, item.isbn)
        if not tx:
            return False, "No active borrow found to return."

        tx.mark_returned()
        user.current_loans.remove(item.isbn)

        # Hand off to next reservation or free up the book
        self._process_next_reservation(item)
        return True, f"Successfully returned '{item.title}'."

    # ─── Revoke ───────────────────────────────────────────────────────────────
    def revoke_borrow(self, user: LibraryUser, item: LibraryItem):
        tx = self._find_active_transaction(user.name, item.isbn)
        if not tx:
            return False, "No active borrow to revoke."

        elapsed = datetime.now() - tx.borrow_date
        if elapsed > timedelta(hours=2):
            return False, "Revoke window (2 hours) has passed."

        tx.revoke()
        user.current_loans.remove(item.isbn)

        # After revoke, offer to next reserver
        self._process_next_reservation(item)
        return True, f"Borrow of '{item.title}' has been revoked."

    # ─── Reserve ──────────────────────────────────────────────────────────────
    def reserve_item(self, user: LibraryUser, item: LibraryItem):
        if user.role == Role.GUEST:
            return False, "Guests cannot place reservations."

        # get or create the queue for this ISBN
        queue = self.reservation_queues.setdefault(item.isbn, [])

        # prevent duplicates
        for r in queue:
            if r.user_name == user.name and r.status in (
                ReservationStatus.PENDING,
                ReservationStatus.ACTIVE,
            ):
                return False, "You already have a reservation."

        # add to queue
        new_res = Reservation(user.name, item.isbn, datetime.now())
        queue.append(new_res)

        # if first in line and book is free, activate hold now
        if len(queue) == 1 and item.status == ItemStatus.AVAILABLE:
            self._activate_hold(item, new_res)

        position = len(queue)
        return True, f"Reserved '{item.title}'. You are number {position} in queue."

    def cancel_reservation(self, user: LibraryUser, item: LibraryItem):
        queue = self.reservation_queues.get(item.isbn, [])
        for idx, res in enumerate(queue):
            if res.user_name == user.name and res.status in (
                ReservationStatus.PENDING,
                ReservationStatus.ACTIVE,
            ):
                res.cancel()
                if idx == 0 and res.status == ReservationStatus.CANCELLED:
                    self._process_next_reservation(item)
                return True, "Your reservation has been cancelled."
        return False, "No active reservation found to cancel."

    # ─── Helpers ───────────────────────────────────────────────────────────────
    def _find_active_transaction(self, user_name, isbn):
        for tx in reversed(self.transactions):
            if (
                tx.user_name == user_name
                and tx.isbn == isbn
                and tx.status == TransactionStatus.ACTIVE
            ):
                return tx
        return None

    def _get_first_active_reservation(self, isbn):
        queue = self.reservation_queues.get(isbn, [])
        for r in queue:
            if r.status == ReservationStatus.ACTIVE:
                return r
        return None

    def _activate_hold(self, item: LibraryItem, reservation: Reservation):
        """Mark a reservation as active and set book status + notify user."""
        reservation.activate_hold()
        item.update_status(ItemStatus.RESERVED)
        
        # Notify the user their reservation is now available
        user = self._find_user_by_name(reservation.user_name)
        NotificationCenter.get_subject().notify('reservation_available', user=user, item=item)


    def _process_next_reservation(self, item: LibraryItem):
        queue = self.reservation_queues.get(item.isbn, [])

        # 1) Expire active hold if it's over
        if queue and queue[0].is_hold_over():
            expired_res = queue[0]
            expired_res.expire()
            from patterns.observer.notification_center import NotificationCenter
            user = self._find_user_by_name(expired_res.user_name)
            NotificationCenter.get_subject().notify('reservation_expired', user=user, item=item)
            queue.pop(0)

        # 2) Promote next pending
        while queue:
            candidate = queue[0]
            if candidate.status == ReservationStatus.PENDING:
                self._activate_hold(item, candidate)
                return
            queue.pop(0)

        item.update_status(ItemStatus.AVAILABLE)

    def _find_user_by_name(self, name: str) -> LibraryUser | None:
        from models.users import active_users
        return active_users.get(name)



def main():
    # ─── Setup ────────────────────────────────────────────────────────────────
    tm = TransactionManager()
    tm1 = TransactionManager()
    print("Singleton test: tm is tm1 ->", tm is tm1)

    gaurav   = LibraryUser("gaurav",   "gaurav@example.com",   "hash1", Role.STUDENT)
    mohsin     = LibraryUser("mohsin",     "mohsin@example.com",     "hash2", Role.FACULTY)
    chandresh = LibraryUser("chandresh", "chandresh@example.com", "hash3", Role.GUEST)

    book = PrintedBook(
        title="1984",
        authors=["George Orwell"],
        isbn="ISBN0001",
        genres=["Dystopian"],
        publication_year=1949,
        language="English",
        status=ItemStatus.AVAILABLE,
        shelf_location="A1"
    )

    print("\n=== Scenario A: Borrow & Revoke ===")
    success, msg = tm.borrow_item(gaurav, book)
    print("gaurav borrows:", msg)
    success, msg = tm.revoke_borrow(gaurav, book)
    print("gaurav revokes  :", msg)
    print("Book status   :", book.status.name)

    print("\n=== Scenario B: Reserve & Borrow Under Hold ===")
    success, msg = tm.reserve_item(gaurav, book)
    print("gaurav reserves:", msg)
    success, msg = tm.reserve_item(mohsin, book)
    print("mohsin reserves  :", msg)
    print("Queue now     :", [str(r) for r in tm.reservation_queues[book.isbn]])

    success, msg = tm.borrow_item(mohsin, book)
    print("mohsin tries to borrow:", msg)

    success, msg = tm.borrow_item(gaurav, book)
    print("gaurav under hold  :", msg)
    print("Queue after borrow :", [str(r) for r in tm.reservation_queues[book.isbn]])
    print("Book status        :", book.status.name)

    success, msg = tm.return_item(gaurav, book)
    print("gaurav returns      :", msg)
    print("Queue now          :", [str(r) for r in tm.reservation_queues.get(book.isbn, [])])
    print("Book status        :", book.status.name)

    success, msg = tm.borrow_item(mohsin, book)
    print("mohsin under new hold :", msg)
    success, msg = tm.return_item(mohsin, book)
    print("mohsin returns        :", msg)
    print("Book status        :", book.status.name)

    print("\n=== Scenario C: Cancel & Expire Holds ===")
    success, msg = tm.reserve_item(gaurav, book)
    print("gaurav reserves:", msg)
    success, msg = tm.reserve_item(mohsin, book)
    print("mohsin reserves  :", msg)
    print("Queue now     :", [str(r) for r in tm.reservation_queues[book.isbn]])

    success, msg = tm.cancel_reservation(gaurav, book)
    print("gaurav cancels :", msg)
    print("Queue now     :", [str(r) for r in tm.reservation_queues[book.isbn]])
    print("Book status   :", book.status.name)

    success, msg = tm.cancel_reservation(mohsin, book)
    print("mohsin cancels   :", msg)
    print("Book status   :", book.status.name)

    # Expiration demo
    success, msg = tm.reserve_item(gaurav, book)
    print("gaurav reserves:", msg)
    # Force the hold to expire immediately
    hold = tm._get_first_active_reservation(book.isbn)
    if hold:
        hold.expiry_date = datetime.now() - timedelta(days=1)
        tm._process_next_reservation(book)

    print("After forced expiry:")
    print("Book status   :", book.status.name)
    print("Queue now     :", tm.reservation_queues.get(book.isbn, []))

    print("\n=== Scenario D: Guest Restrictions ===")
    success, msg = tm.reserve_item(chandresh, book)
    print("chandresh reserves:", msg)
    success, msg = tm.borrow_item(chandresh, book)
    print("chandresh borrows :", msg)


if __name__ == "__main__":
    main()