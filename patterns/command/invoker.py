from patterns.command.commands import BorrowCommand, ReturnCommand, ReserveCommand
from models.items import PrintedBook, ItemStatus
from models.users import LibraryUser, Role

class CommandInvoker:
    def __init__(self):
        self.history = []

    def execute_command(self, command):
        command.execute()
        self.history.append(command)

    def undo_last(self):
        if not self.history:
            print("No commands to undo.")
            return
        last_command = self.history.pop()
        last_command.undo()

    def undo_all(self):
        while self.history:
            self.undo_last()

def main():
    invoker = CommandInvoker()

    # Users
    gaurav = LibraryUser("Gaurav", "gaurav@lib.com", "pass123", Role.STUDENT)
    mohsin = LibraryUser("Mohsin", "mohsin@lib.com", "pass123", Role.FACULTY)
    chandresh = LibraryUser("Chandresh", "chandresh@lib.com", "pass123", Role.STUDENT)

    # Items
    clean_code = PrintedBook(
        title="Clean Code",
        authors=["Uncle Bob"],
        isbn="ISBN001",
        genres=["Programming"],
        publication_year=2008,
        language="English",
        status=ItemStatus.AVAILABLE,
        shelf_location="A1"
    )

    design_patterns = PrintedBook(
        title="Design Patterns",
        authors=["GoF"],
        isbn="ISBN002",
        genres=["Software Engineering"],
        publication_year=1994,
        language="English",
        status=ItemStatus.AVAILABLE,
        shelf_location="B2"
    )

    print("\n--- Gaurav borrows 'Clean Code' ---")
    borrow_cmd = BorrowCommand(gaurav, clean_code)
    invoker.execute_command(borrow_cmd)

    print("\n--- Gaurav returns 'Clean Code' ---")
    return_cmd = ReturnCommand(gaurav, clean_code)
    invoker.execute_command(return_cmd)

    print("\n--- Mohsin reserves 'Design Patterns' ---")
    reserve_cmd = ReserveCommand(mohsin, design_patterns)
    invoker.execute_command(reserve_cmd)

    print("\n--- Undo last action (cancel Mohsin's reservation) ---")
    invoker.undo_last()

    print("\n--- Chandresh borrows 'Design Patterns' ---")
    borrow2_cmd = BorrowCommand(chandresh, design_patterns)
    invoker.execute_command(borrow2_cmd)

    print("\n--- Undo ALL actions in reverse order ---")
    invoker.undo_all()


if __name__ == "__main__":
    main()