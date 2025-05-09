from models.items import LibraryItem, EBook, PrintedBook, ResearchPaper, Audiobook
from models.items import ItemStatus
from typing import List, Optional

class LibraryItemBuilder:
    def __init__(self):
        self._title: Optional[str] = None
        self._authors: List[str] = []
        self._isbn: Optional[str] = None
        self._genres: List[str] = []
        self._publication_year: Optional[int] = None
        self._language: Optional[str] = None
        self._status: ItemStatus = ItemStatus.AVAILABLE

    def with_title(self, title: str):
        self._title = title
        return self

    def add_author(self, author: str):
        self._authors.append(author)
        return self

    def set_authors(self, authors: List[str]):
        self._authors = authors
        return self

    def add_genre(self, genre: str):
        self._genres.append(genre)
        return self

    def set_genres(self, genres: List[str]):
        self._genres = genres
        return self

    def with_isbn(self, isbn: str):
        self._isbn = isbn
        return self

    def with_publication_year(self, year: int):
        self._publication_year = year
        return self

    def with_language(self, language: str):
        self._language = language
        return self

    def with_status(self, status: ItemStatus):
        self._status = status
        return self

    def _validate_base_fields(self):
        if not self._title:
            raise ValueError("Title is required")
        if not self._authors:
            raise ValueError("At least one author is required")
        if not self._isbn:
            raise ValueError("ISBN is required")
        if not self._genres:
            raise ValueError("At least one genre is required")
        if not self._publication_year:
            raise ValueError("Publication year is required")
        if not self._language:
            raise ValueError("Language is required")


# ---- Specialized Builders ---- #

class EBookBuilder(LibraryItemBuilder):
    def __init__(self):
        super().__init__()
        self._file_format: Optional[str] = None

    def with_file_format(self, file_format: str):
        self._file_format = file_format
        return self

    def build(self) -> EBook:
        self._validate_base_fields()
        if not self._file_format:
            raise ValueError("File format is required for an EBook")

        return EBook(
            title=self._title,
            authors=self._authors,
            isbn=self._isbn,
            genres=self._genres,
            publication_year=self._publication_year,
            language=self._language,
            status=self._status,
            file_format=self._file_format
        )


class PrintedBookBuilder(LibraryItemBuilder):
    def __init__(self):
        super().__init__()
        self._shelf_location: Optional[str] = None

    def with_shelf_location(self, location: str):
        self._shelf_location = location
        return self

    def build(self) -> PrintedBook:
        self._validate_base_fields()
        if not self._shelf_location:
            raise ValueError("Shelf location is required for a PrintedBook")

        return PrintedBook(
            title=self._title,
            authors=self._authors,
            isbn=self._isbn,
            genres=self._genres,
            publication_year=self._publication_year,
            language=self._language,
            status=self._status,
            shelf_location=self._shelf_location
        )


class AudiobookBuilder(LibraryItemBuilder):
    def __init__(self):
        super().__init__()
        self._duration_minutes: Optional[int] = None

    def with_duration(self, minutes: int):
        self._duration_minutes = minutes
        return self

    def build(self) -> Audiobook:
        self._validate_base_fields()
        if self._duration_minutes is None:
            raise ValueError("Duration is required for an Audiobook")

        return Audiobook(
            title=self._title,
            authors=self._authors,
            isbn=self._isbn,
            genres=self._genres,
            publication_year=self._publication_year,
            language=self._language,
            status=self._status,
            duration_minutes=self._duration_minutes
        )


class ResearchPaperBuilder(LibraryItemBuilder):
    def __init__(self):
        super().__init__()
        self._journal: Optional[str] = None

    def with_journal(self, journal: str):
        self._journal = journal
        return self

    def build(self) -> ResearchPaper:
        self._validate_base_fields()
        if not self._journal:
            raise ValueError("Journal is required for a ResearchPaper")

        return ResearchPaper(
            title=self._title,
            authors=self._authors,
            isbn=self._isbn,
            genres=self._genres,
            publication_year=self._publication_year,
            language=self._language,
            status=self._status,
            journal=self._journal
        )


# -------------------------- #
# Main Function to Cover Scenarios
# -------------------------- #

def main():
    # EBook Example
    ebook = EBookBuilder().with_title("1984") \
        .set_authors(["George Orwell"]) \
        .with_isbn("9780451524935") \
        .set_genres(["Dystopian", "Fiction"]) \
        .with_publication_year(1949) \
        .with_language("English") \
        .with_file_format("PDF") \
        .with_status(ItemStatus.AVAILABLE) \
        .build()

    print(ebook)

    # PrintedBook Example
    printed_book = PrintedBookBuilder().with_title("Moby Dick") \
        .set_authors(["Herman Melville"]) \
        .with_isbn("9781851244422") \
        .set_genres(["Fiction", "Adventure"]) \
        .with_publication_year(1851) \
        .with_language("English") \
        .with_shelf_location("Shelf A1") \
        .with_status(ItemStatus.AVAILABLE) \
        .build()

    print(printed_book)

    # Audiobook Example
    audiobook = AudiobookBuilder().with_title("The Hobbit") \
        .set_authors(["J.R.R. Tolkien"]) \
        .with_isbn("9780345339683") \
        .set_genres(["Fantasy", "Adventure"]) \
        .with_publication_year(1937) \
        .with_language("English") \
        .with_duration(300) \
        .with_status(ItemStatus.CHECKED_OUT) \
        .build()

    print(audiobook)

    # ResearchPaper Example
    research_paper = ResearchPaperBuilder().with_title("Quantum Computing") \
        .set_authors(["John Doe", "Jane Smith"]) \
        .with_isbn("9780123456789") \
        .set_genres(["Science", "Technology"]) \
        .with_publication_year(2021) \
        .with_language("English") \
        .with_journal("Nature") \
        .with_status(ItemStatus.AVAILABLE) \
        .build()

    print(research_paper)

if __name__ == "__main__":
    main()
