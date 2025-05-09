from patterns.command.commands import BorrowCommand, ReturnCommand, ReserveCommand
from patterns.command.invoker import CommandInvoker
from models.items import *
from models.users import *

class LibraryFacade:
    def __init__(self):
        self.invoker = CommandInvoker()

    def borrow_book(self, user: LibraryUser, item: LibraryItem):
        cmd = BorrowCommand(user, item)
        self.invoker.execute_command(cmd)

    def return_book(self, user: LibraryUser, item: LibraryItem):
        cmd = ReturnCommand(user, item)
        self.invoker.execute_command(cmd)

    def reserve_book(self, user: LibraryUser, item: LibraryItem):
        cmd = ReserveCommand(user, item)
        self.invoker.execute_command(cmd)

    def undo_last_action(self):
        self.invoker.undo_last()

    def undo_all_actions(self):
        self.invoker.undo_all()
        
def main():
    facade = LibraryFacade()

    # Users
    gaurav = LibraryUser("Gaurav", "g@x.com", "h", Role.STUDENT)
    mohsin = LibraryUser("Mohsin", "m@x.com", "h", Role.FACULTY)

    # Items
    book = PrintedBook("1984", ["Orwell"], "ISBN0001", ["Dystopia"], 1949, "English", ItemStatus.AVAILABLE, "A1")
    active_items.append(book)

  # 1) Student borrows
    facade.borrow_book(gaurav, book)

    # 2) Student returns
    facade.return_book(gaurav, book)

    # 3) Student reserves
    facade.reserve_book(gaurav, book)

    # 4) Faculty borrows—even though reserved
    facade.borrow_book(mohsin, book)

    # 5) Undo that last faculty borrow
    facade.undo_last_action()

    # 6) Return book so the original reserver (gaurav) gets the hold again
    facade.return_book(mohsin, book)

    # 7) Undo all outstanding commands
    facade.undo_all_actions()
if __name__ == "__main__":
    main()