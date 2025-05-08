from abc import ABC, abstractmethod
from enum import Enum, auto

class ItemStatus(Enum):
    AVAILABLE = auto()
    CHECKED_OUT = auto()
    RESERVED = auto()
    UNDER_REVIEW = auto()

class LibraryItem(ABC):
    def __init__(self, title: str, authors: list[str], isbn: str):
        self.title = title
        self.authors = authors
        self.isbn = isbn
        self.status = ItemStatus.AVAILABLE

    @abstractmethod
    def item_type(self) -> str:
        pass

    def __str__(self):
        return f"[{self.item_type()}] {self.title} (ISBN: {self.isbn}) - Status: {self.status.name}"

    def update_status(self, new_status: ItemStatus):
        if not isinstance(new_status, ItemStatus):
            raise ValueError("Invalid status type")
        self.status = new_status

class EBook(LibraryItem):
    def __init__(self, title: str, authors: list[str], isbn: str, file_format: str):
        super().__init__(title, authors, isbn)
        self.file_format = file_format

    def item_type(self) -> str:
        return "E-Book"


class PrintedBook(LibraryItem):
    def __init__(self, title: str, authors: list[str], isbn: str, shelf_location: str):
        super().__init__(title, authors, isbn)
        self.shelf_location = shelf_location

    def item_type(self) -> str:
        return "Printed Book"


class ResearchPaper(LibraryItem):
    def __init__(self, title: str, authors: list[str], isbn: str, journal: str, year: int):
        super().__init__(title, authors, isbn)
        self.journal = journal
        self.year = year

    def item_type(self) -> str:
        return "Research Paper"


class Audiobook(LibraryItem):
    def __init__(self, title: str, authors: list[str], isbn: str, duration_minutes: int):
        super().__init__(title, authors, isbn)
        self.duration_minutes = duration_minutes

    def item_type(self) -> str:
        return "Audiobook"
