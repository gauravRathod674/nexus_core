from abc import ABC, abstractmethod
from datetime import datetime

from utils.dummy_data import get_dummy_transactions, get_dummy_users
from models.transactions import BorrowingTransaction, TransactionStatus
from models.users import LibraryUser, Role



class LateFeePolicy(ABC):
    @abstractmethod
    def compute(self, days_overdue: float, user: LibraryUser, demand: int) -> float:
        ...


class RoleBasedPolicy(LateFeePolicy):
    BASE_RATES = {
        Role.STUDENT: 5.0,
        Role.RESEARCHER: 4.0,
        Role.FACULTY: 1.0,
        Role.LIBRARIAN: 3.0
    }
    def compute(self, days_overdue, user, demand):
        return self.BASE_RATES.get(user.role, 5.0) * days_overdue


class DemandSurchargePolicy(LateFeePolicy):
    def __init__(self, wrapped: LateFeePolicy, surcharge_per_user: float = 0.1):
        self._wrapped = wrapped
        self._surcharge_per_user = surcharge_per_user

    def compute(self, days_overdue, user, demand):
        base = self._wrapped.compute(days_overdue, user, demand)
        return round(base * (1 + self._surcharge_per_user * demand), 2)



class LateFeeCalculator:
    def __init__(self, policy: LateFeePolicy):
        self._policy = policy

    def calculate(self, tx: BorrowingTransaction, user: LibraryUser, demand: int) -> float:
        if tx.status in {TransactionStatus.RETURNED, TransactionStatus.COMPLETED, TransactionStatus.REVOKED}:
            return 0.0

        now = datetime.now()

        # Case A: already returned late
        if tx.return_date and tx.return_date > tx.due_date:
            overdue_seconds = (tx.return_date - tx.due_date).total_seconds()

        # Case B: still out and overdue
        elif now > tx.due_date:
            overdue_seconds = (now - tx.due_date).total_seconds()

        else:
            return 0.0

        # convert to days (fractional)
        days_overdue = overdue_seconds / 86400
        return self._policy.compute(days_overdue, user, demand)



def main():
    transactions = get_dummy_transactions()
    users = {u.name: u for u in get_dummy_users()}

    demand_counts = {tx.isbn: idx % 3 for idx, tx in enumerate(transactions)}

    policy = DemandSurchargePolicy(RoleBasedPolicy(), surcharge_per_user=0.1)
    calc = LateFeeCalculator(policy)

    print("=== Late Fee Report (₹) ===")
    for tx in transactions:
        user = users.get(tx.user_name)
        fee = calc.calculate(tx, user, demand_counts.get(tx.isbn, 0))
        print(f"{user.name} [{tx.status.name}]: ISBN {tx.isbn}, Fee=₹{fee}")

if __name__ == "__main__":
    main()
