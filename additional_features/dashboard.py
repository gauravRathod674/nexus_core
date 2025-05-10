# additional_features/dashboard.py

from datetime import datetime
from typing import List
from models.transactions import TransactionStatus
from models.users import Role, LibraryUser
from models.items import LibraryItem, ItemStatus
from patterns.singleton.transaction_manager import TransactionManager
from patterns.state.item_state import (
    AvailableState,
    CheckedOutState,
    ReservedState,
    UnderReviewState,
)
from utils.config import BORROW_LIMITS, BORROW_DURATIONS


def _attach_state(item: LibraryItem):
    if item.status == ItemStatus.AVAILABLE:
        item._state = AvailableState()
    elif item.status == ItemStatus.CHECKED_OUT:
        item._state = CheckedOutState()
    elif item.status == ItemStatus.RESERVED:
        item._state = ReservedState()
    else:
        item._state = UnderReviewState()


def check_availability(items: List[LibraryItem]):
    isbn = input("Enter ISBN to check: ").strip()
    found = next((it for it in items if it.isbn == isbn), None)
    if not found:
        print("📖 No such ISBN in catalog.")
        return
    _attach_state(found)
    print(f"Status of '{found.title}': {found.status.name}")


def list_overdue(user: LibraryUser, transactions: List):
    print(f"\n🚨 Overdue Loans for {user.name}:")
    now = datetime.now()
    any_found = False
    for tx in transactions:
        if tx.user_name != user.name:
            continue
        if tx.status == TransactionStatus.OVERDUE or (
            tx.status == TransactionStatus.ACTIVE and now > tx.due_date
        ):
            days = (now - tx.due_date).days
            print(
                f" - ISBN {tx.isbn}, due on {tx.due_date.date()} ({days} days overdue)"
            )
            any_found = True
    if not any_found:
        print("No overdue items.")


def view_profile(user: LibraryUser, items: List[LibraryItem]):
    print(f"\n👤 Profile: {user.name}")
    print(f"  Role          : {user.role.name}")
    print(f"  Borrow limit  : {user.get_borrow_limit()} items")
    print(f"  Loan duration : {user.get_borrow_duration()} days")
    print(f"  Currently loaned ISBNs: {user.current_loans or 'None'}")
    for isbn in user.current_loans:
        title = next((it.title for it in items if it.isbn == isbn), "Unknown")
        print(f"    - {title} ({isbn})")


def manage_lending_policies():
    print("\n🔧 Manage Lending Policies")
    roles = list(BORROW_LIMITS.keys())
    for idx, role in enumerate(roles, start=1):
        print(
            f" {idx}) {role.name}: limit={BORROW_LIMITS[role]}, duration={BORROW_DURATIONS[role]}"
        )
    print(f" {len(roles)+1}) Back")
    sel = input(f"Select role [1-{len(roles)+1}]: ").strip()
    if not sel.isdigit():
        print("❌ Invalid input.")
        return
    sel = int(sel)
    if sel == len(roles) + 1:
        return
    if not (1 <= sel <= len(roles)):
        print("❌ Out of range.")
        return
    role = roles[sel - 1]
    try:
        new_limit = int(input(f"New borrow limit for {role.name}: ").strip())
        new_dur = int(input(f"New borrow duration for {role.name}: ").strip())
    except ValueError:
        print("❌ Must enter integer values.")
        return
    BORROW_LIMITS[role] = new_limit
    BORROW_DURATIONS[role] = new_dur
    print(f"✔ Updated {role.name}: limit={new_limit}, duration={new_dur} days.")


def manage_user_roles(users: List[LibraryUser]):
    from models.users import Role

    print("\n👥 Manage User Roles")
    for idx, u in enumerate(users, start=1):
        print(f" {idx}) {u.name}: current role = {u.role.name}")
    sel = input("Select user number: ").strip()
    if not sel.isdigit() or not (1 <= int(sel) <= len(users)):
        print("❌ Invalid selection.")
        return
    user = users[int(sel) - 1]
    roles = list(Role)
    print(f"Selected {user.name}. Available roles:")
    for idx, role in enumerate(roles, start=1):
        print(f" {idx}) {role.name}")
    rsel = input("Select new role number: ").strip()
    if not rsel.isdigit() or not (1 <= int(rsel) <= len(roles)):
        print("❌ Invalid role selection.")
        return
    user.role = roles[int(rsel) - 1]
    print(f"✔ Role updated: {user.name} is now {user.role.name}.")


def process_return(
    tm: TransactionManager, users: List[LibraryUser], items: List[LibraryItem]
):
    open_tx = [
        tx
        for tx in tm.transactions
        if tx.status in {TransactionStatus.ACTIVE, TransactionStatus.OVERDUE}
    ]
    if not open_tx:
        print("\n🔄 No active or overdue loans to process.")
        return
    print("\n🔄 Process a Return")
    for idx, tx in enumerate(open_tx, start=1):
        print(f" {idx}) {tx.user_name} | ISBN {tx.isbn} | Status {tx.status.name}")
    sel = input(f"Select transaction [1-{len(open_tx)}]: ").strip()
    if not sel.isdigit() or not (1 <= int(sel) <= len(open_tx)):
        print("❌ Invalid selection.")
        return
    tx = open_tx[int(sel) - 1]
    usr = next((u for u in users if u.name == tx.user_name), None)
    item = next((i for i in items if i.isbn == tx.isbn), None)
    ok, msg = tm.return_item(usr, item)
    print(("✔" if ok else "✘"), msg)
