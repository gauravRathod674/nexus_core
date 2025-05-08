from datetime import datetime, timedelta
from enum import Enum, auto


class TransactionStatus(Enum):
    ACTIVE = auto()
    COMPLETED = auto()
    OVERDUE = auto()
    RETURNED = auto()
    REVOKED = auto()


class BorrowingTransaction:
    def __init__(self, user_name: str, isbn: str, borrow_date: datetime, period_days: int):
        self.user_name = user_name
        self.isbn = isbn
        self.borrow_date = borrow_date
        self.due_date = borrow_date + timedelta(days=period_days)
        self.return_date: datetime | None = None
        self.status = TransactionStatus.ACTIVE

    def mark_returned(self, return_date: datetime = None):
        self.return_date = return_date or datetime.now()
        self.status = TransactionStatus.RETURNED

    def revoke(self):
        if self.status == TransactionStatus.ACTIVE and (datetime.now() - self.borrow_date) <= timedelta(hours=2):
            self.status = TransactionStatus.REVOKED
            self.return_date = datetime.now()
        else:
            raise Exception("Revoke action is only allowed within 2 hours of borrowing and if transaction is still active.")

    def complete_transaction(self):
        self.status = TransactionStatus.COMPLETED
        self.return_date = datetime.now()

        # Example placeholder for notifying next reserver
        # notify_next_user_in_queue(self.isbn)

    def is_overdue(self) -> bool:
        if self.status != TransactionStatus.ACTIVE:
            return False
        return datetime.now() > self.due_date

    def calculate_late_fee(self) -> float:
        if self.return_date and self.return_date > self.due_date:
            delay = self.return_date - self.due_date
            return delay.total_seconds() / 3600  # hourly fee base
        return 0.0

    def __str__(self):
        return (
            f"Transaction(user={self.user_name}, isbn={self.isbn}, "
            f"borrowed={self.borrow_date.date()}, due={self.due_date.date()}, status={self.status.name})"
        )
 