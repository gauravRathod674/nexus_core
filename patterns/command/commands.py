from abc import ABC, abstractmethod
from patterns.singleton.transaction_manager import TransactionManager

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass


class BorrowCommand(Command):
    def __init__(self, user, item):
        self.user = user
        self.item = item
        self.success = False
        self.manager = TransactionManager()

    def execute(self):
        self.success, msg = self.manager.borrow_item(self.user, self.item)
        print(msg)

    def undo(self):
        if self.success:
            success, msg = self.manager.revoke_borrow(self.user, self.item)
            print(f"Undo: {msg}")


class ReturnCommand(Command):
    def __init__(self, user, item):
        self.user = user
        self.item = item
        self.success = False
        self.manager = TransactionManager()

    def execute(self):
        self.success, msg = self.manager.return_item(self.user, self.item)
        print(msg)

    def undo(self):
        if self.success:
            success, msg = self.manager.borrow_item(self.user, self.item)
            print(f"Undo: {msg}")


class ReserveCommand(Command):
    def __init__(self, user, item):
        self.user = user
        self.item = item
        self.success = False
        self.manager = TransactionManager()

    def execute(self):
        self.success, msg = self.manager.reserve_item(self.user, self.item)
        print(msg)

    def undo(self):
        if self.success:
            success, msg = self.manager.cancel_reservation(self.user, self.item)
            print(f"Undo: {msg}")
