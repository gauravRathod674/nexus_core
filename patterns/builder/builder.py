# utils/builders.py
from abc import ABC, abstractmethod
from models.items import LibraryItem, EBook, PrintedBook, ResearchPaper, Audiobook
from models.items import ItemStatus


class LibraryItemBuilder(ABC):
    def __init__(self):
        self._title = None
        self._authors = []
        self._isbn = None
        self._status = ItemStatus.AVAILABLE

    def with_title(self, title: str):
        self._title = title
        return self

    def with_authors(self, authors: list[str]):
        self._authors = authors
        return self

    def with_isbn(self, isbn: str):
        self._isbn = isbn
        return self

    def with_status(self, status: ItemStatus):
        self._status = status
        return self

    @abstractmethod
    def build(self) -> LibraryItem:
        """Constructs and returns the concrete LibraryItem."""
        ...


class EBookBuilder(LibraryItemBuilder):
    def __init__(self):
        super().__init__()
        self._file_format = None

    def with_file_format(self, fmt: str):
        self._file_format = fmt
        return self

    def build(self) -> EBook:
        ebook = EBook(
            title=self._title,
            authors=self._authors,
            isbn=self._isbn,
            file_format=self._file_format,
        )
        ebook.status = self._status
        return ebook


class PrintedBookBuilder(LibraryItemBuilder):
    def __init__(self):
        super().__init__()
        self._shelf_location = None

    def with_shelf_location(self, loc: str):
        self._shelf_location = loc
        return self

    def build(self) -> PrintedBook:
        pb = PrintedBook(
            title=self._title,
            authors=self._authors,
            isbn=self._isbn,
            shelf_location=self._shelf_location,
        )
        pb.status = self._status
        return pb


class ResearchPaperBuilder(LibraryItemBuilder):
    def __init__(self):
        super().__init__()
        self._journal = None
        self._year = None

    def with_journal(self, journal: str):
        self._journal = journal
        return self

    def with_year(self, year: int):
        self._year = year
        return self

    def build(self) -> ResearchPaper:
        rp = ResearchPaper(
            title=self._title,
            authors=self._authors,
            isbn=self._isbn,
            journal=self._journal,
            year=self._year,
        )
        rp.status = self._status
        return rp


class AudiobookBuilder(LibraryItemBuilder):
    def __init__(self):
        super().__init__()
        self._duration_minutes = None

    def with_duration_minutes(self, mins: int):
        self._duration_minutes = mins
        return self

    def build(self) -> Audiobook:
        ab = Audiobook(
            title=self._title,
            authors=self._authors,
            isbn=self._isbn,
            duration_minutes=self._duration_minutes,
        )
        ab.status = self._status
        return ab


class ItemDirector:
    """Optional helper for common presets."""
    @staticmethod
    def classic_ebook():
        return (
            EBookBuilder()
            .with_title("Classic Tales")
            .with_authors(["John Doe"])
            .with_isbn("000-CLASSIC")
            .with_file_format("PDF")
            .build()
        )

    @staticmethod
    def standard_printed_book():
        return (
            PrintedBookBuilder()
            .with_title("Standard Book")
            .with_authors(["Jane Doe"])
            .with_isbn("111-STD")
            .with_shelf_location("C1-01")
            .build()
        )


def main():
    # Build one of each type
    ebook = (
        EBookBuilder()
        .with_title("Deep Learning with Python")
        .with_authors(["Francois Chollet"])
        .with_isbn("9781617294433")
        .with_file_format("PDF")
        .build()
    )

    printed = (
        PrintedBookBuilder()
        .with_title("Clean Code")
        .with_authors(["Robert C. Martin"])
        .with_isbn("9780132350884")
        .with_shelf_location("A3-42")
        .build()
    )

    paper = (
        ResearchPaperBuilder()
        .with_title("Attention Is All You Need")
        .with_authors(["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"])
        .with_isbn("10.48550/arXiv.1706.03762")
        .with_journal("NeurIPS")
        .with_year(2017)
        .build()
    )

    audio = (
        AudiobookBuilder()
        .with_title("The Hobbit")
        .with_authors(["J.R.R. Tolkien"])
        .with_isbn("9780261103344")
        .with_duration_minutes(720)
        .build()
    )

    # Preset examples
    classic = ItemDirector.classic_ebook()
    standard = ItemDirector.standard_printed_book()

    print("=== Built Items ===")
    for item in [ebook, printed, paper, audio, classic, standard]:
        print(item)


if __name__ == "__main__":
    main()
