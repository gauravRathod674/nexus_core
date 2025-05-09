from functools import wraps
from patterns.observer.notification_center import NotificationCenter
from models.reservation import Reservation, ReservationStatus
from models.users import Role
from datetime import datetime

def with_due_date_reminder(func):
    """Decorator to trigger due date reminder check after borrow/return."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        # Simulate checking due dates (in real systems, this would trigger async job)
        from models.transactions import BorrowingTransaction
        from patterns.singleton.transaction_manager import TransactionManager
        tm = TransactionManager()
        for tx in tm.transactions:
            if tx.is_overdue():
                user = tm._find_user_by_name(tx.user_name)
                item = next((i for i in tm._get_all_items() if i.isbn == tx.isbn), None)
                if user and item:
                    NotificationCenter.get_subject().notify(
                        "due_date_approaching",
                        user=user,
                        item=item,
                        due_date=tx.due_date.date()
                    )
        return result
    return wrapper


def with_priority_borrowing(func):
    """Decorator to prioritize faculty members during borrowing."""
    @wraps(func)
    def wrapper(user, item, *args, **kwargs):
        from patterns.singleton.transaction_manager import TransactionManager
        tm = TransactionManager()
        queue = tm.reservation_queues.get(item.isbn, [])
        first_hold = tm._get_first_active_reservation(item.isbn)

        if item.status == item.status.RESERVED and first_hold and first_hold.user_name != user.name:
            if user.role == Role.FACULTY:
                # Remove faculty member's earlier reservation if any
                queue = [res for res in queue if res.user_name != user.name]
                tm.reservation_queues[item.isbn] = queue
                # Skip to front of queue
                item.update_status(item.status.AVAILABLE)

        return func(user, item, *args, **kwargs)
    return wrapper
