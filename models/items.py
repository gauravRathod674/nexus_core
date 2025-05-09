from enum import Enum
from typing import List
from abc import ABC, abstractmethod


class ItemStatus(Enum):
    AVAILABLE = "Available"
    CHECKED_OUT = "Checked Out"
    RESERVED = "Reserved"
    UNDER_REVIEW = "Under Review"


class LibraryItem(ABC):
    def __init__(
        self,
        title: str,
        authors: List[str],
        isbn: str,
        genres: List[str],
        publication_year: int,
        language: str,
        status: ItemStatus = ItemStatus.AVAILABLE
    ):
        self.title = title
        self.authors = authors
        self.isbn = isbn
        self.genres = genres
        self.publication_year = publication_year
        self.language = language
        self.status = status
        
        from patterns.state.item_state import AvailableState

        self._state = AvailableState()

    @abstractmethod
    def item_type(self) -> str:
        pass

    def update_status(self, new_status: ItemStatus):
        self.status = new_status

    def borrow(self, user):
        return self._state.borrow(self, user)

    def return_item(self, user):
        return self._state.return_item(self, user)

    def reserve(self, user):
        return self._state.reserve(self, user)


class EBook(LibraryItem):
    def __init__(
        self,
        title: str,
        authors: List[str],
        isbn: str,
        genres: List[str],
        publication_year: int,
        language: str,
        status: ItemStatus,
        file_format: str,
    ):
        super().__init__(
            title, authors, isbn, genres, publication_year, language, status
        )
        self.file_format = file_format

    def item_type(self) -> str:
        return "E-Book"

    def __str__(self) -> str:
        return f"{super().__str__()}, Format: {self.file_format}"


class PrintedBook(LibraryItem):
    def __init__(
        self,
        title: str,
        authors: List[str],
        isbn: str,
        genres: List[str],
        publication_year: int,
        language: str,
        status: ItemStatus,
        shelf_location: str,
    ):
        super().__init__(
            title, authors, isbn, genres, publication_year, language, status
        )
        self.shelf_location = shelf_location

    def item_type(self) -> str:
        return "Printed Book"

    def __str__(self) -> str:
        return f"{super().__str__()}, Shelf: {self.shelf_location}"


class Audiobook(LibraryItem):
    def __init__(
        self,
        title: str,
        authors: List[str],
        isbn: str,
        genres: List[str],
        publication_year: int,
        language: str,
        status: ItemStatus,
        duration_minutes: int,
    ):
        super().__init__(
            title, authors, isbn, genres, publication_year, language, status
        )
        self.duration_minutes = duration_minutes

    def item_type(self) -> str:
        return "Audiobook"

    def __str__(self) -> str:
        return f"{super().__str__()}, Duration: {self.duration_minutes} mins"


class ResearchPaper(LibraryItem):
    def __init__(
        self,
        title: str,
        authors: List[str],
        isbn: str,
        genres: List[str],
        publication_year: int,
        language: str,
        status: ItemStatus,
        journal: str,
    ):
        super().__init__(
            title, authors, isbn, genres, publication_year, language, status
        )
        self.journal = journal

    def item_type(self) -> str:
        return "Research Paper"

    def __str__(self) -> str:
        return f"{super().__str__()}, Journal: {self.journal}"
