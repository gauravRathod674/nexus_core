from functools import wraps
from datetime import datetime, timedelta
from patterns.observer.notification_center import NotificationCenter
from models.users import Role
from models.items import ItemStatus

def with_priority_borrowing(func):
    @wraps(func)
    def wrapper(self, user, item, *args, **kwargs):
        # import here, not at top
        from patterns.singleton.transaction_manager import TransactionManager
        tm = TransactionManager()

        queue = tm.reservation_queues.get(item.isbn, [])
        first_hold = tm._get_first_active_reservation(item.isbn)

        # If reserved by someone else, Faculty skips to front
        if item.status == ItemStatus.RESERVED and first_hold and first_hold.user_name != user.name:
            if user.role == Role.FACULTY:
                # remove any existing faculty reservation
                tm.reservation_queues[item.isbn] = [r for r in queue if r.user_name != user.name]
                # free up the book
                item.update_status(ItemStatus.AVAILABLE)

        return func(self, user, item, *args, **kwargs)
    return wrapper


def with_due_date_reminder(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)

        # import here too
        from patterns.singleton.transaction_manager import TransactionManager
        tm = TransactionManager()

        # scan for any tx due in 1 day
        for tx in tm.transactions:
            if tx.status.name == "ACTIVE":
                days_left = (tx.due_date - datetime.now()).days
                if days_left == 1:
                    user = tm._find_user_by_name(tx.user_name)
                    # find item by ISBN
                    from models.items import active_items
                    item = next((i for i in active_items if i.isbn == tx.isbn), None)
                    if user and item:
                        NotificationCenter.get_subject().notify(
                            "due_date_approaching",
                            user=user,
                            item=item,
                            due_date=tx.due_date.date()
                        )
        return result
    return wrapper
