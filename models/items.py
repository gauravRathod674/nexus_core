from abc import ABC, abstractmethod
from typing import List
from enum import Enum

# Enum for item status
class ItemStatus(Enum):
    AVAILABLE = "Available"
    CHECKED_OUT = "Checked Out"
    RESERVED = "Reserved"
    UNDER_REVIEW = "Under Review"


# Base class for all library items
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
    
    @abstractmethod
    def item_type(self) -> str:
        pass
    
    def __str__(self):
        genres_str = ", ".join(self.genres)
        return (
            f"[{self.item_type()}] {self.title} (ISBN: {self.isbn})\n"
            f"  Authors: {', '.join(self.authors)} | Year: {self.publication_year} | "
            f"Language: {self.language} | Genres: {genres_str} | Status: {self.status.name}"
        )

    def update_status(self, new_status: ItemStatus):
        if not isinstance(new_status, ItemStatus):
            raise ValueError("Invalid status type")
        self.status = new_status


# Subclass for EBooks
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
        file_format: str
    ):
        super().__init__(title, authors, isbn, genres, publication_year, language, status)
        self.file_format = file_format

    def __str__(self):
        return f"{super().__str__()}, Format: {self.file_format}"

    def item_type(self) -> str:
        return "E-Book"


# Subclass for PrintedBooks
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
        shelf_location: str
    ):
        super().__init__(title, authors, isbn, genres, publication_year, language, status)
        self.shelf_location = shelf_location

    def __str__(self):
        return f"{super().__str__()}, Shelf: {self.shelf_location}"

    def item_type(self) -> str:
        return "Printed Book"


# Subclass for Audiobooks
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
        duration_minutes: int
    ):
        super().__init__(title, authors, isbn, genres, publication_year, language, status)
        self.duration_minutes = duration_minutes

    def __str__(self):
        return f"{super().__str__()}, Duration: {self.duration_minutes} mins"

    def item_type(self) -> str:
        return "Audiobook"


# Subclass for ResearchPapers
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
        journal: str
    ):
        super().__init__(title, authors, isbn, genres, publication_year, language, status)
        self.journal = journal

    def __str__(self):
        return f"{super().__str__()}, Journal: {self.journal}"

    def item_type(self) -> str:
        return "Research Paper"
