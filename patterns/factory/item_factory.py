from typing import Type, Dict
from models.items import LibraryItem, EBook, PrintedBook, ResearchPaper, Audiobook, ItemStatus

class LibraryItemFactory:
    _registered_item_classes: Dict[str, Type[LibraryItem]] = {}

    @staticmethod
    def register(item_type_key: str, item_class: Type[LibraryItem]):
        item_type_key = item_type_key.lower()
        LibraryItemFactory._registered_item_classes[item_type_key] = item_class

    @staticmethod
    def create(item_type_key: str, **item_data) -> LibraryItem:
        item_type_key = item_type_key.lower()
        item_class = LibraryItemFactory._registered_item_classes.get(item_type_key)

        if not item_class:
            raise ValueError(f"Item type '{item_type_key}' is not registered.")

        return item_class(**item_data)


def main():
    # Register item types
    LibraryItemFactory.register("ebook", EBook)
    LibraryItemFactory.register("printedbook", PrintedBook)
    LibraryItemFactory.register("researchpaper", ResearchPaper)
    LibraryItemFactory.register("audiobook", Audiobook)

    # Create a few items with complete required parameters
    ebook = LibraryItemFactory.create(
        "ebook",
        title="Deep Learning with Python",
        authors=["François Chollet"],
        isbn="9781617294433",
        genres=["AI", "Machine Learning"],
        publication_year=2017,
        language="English",
        status=ItemStatus.AVAILABLE,
        file_format="PDF"
    )

    printed = LibraryItemFactory.create(
        "printedbook",
        title="Clean Code",
        authors=["Robert C. Martin"],
        isbn="9780132350884",
        genres=["Programming", "Software Engineering"],
        publication_year=2008,
        language="English",
        status=ItemStatus.AVAILABLE,
        shelf_location="A2-15"
    )

    paper = LibraryItemFactory.create(
        "researchpaper",
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
        isbn="1234567890123",
        genres=["AI", "NLP"],
        publication_year=2017,
        language="English",
        status=ItemStatus.AVAILABLE,
        journal="NIPS"
    )

    audio = LibraryItemFactory.create(
        "audiobook",
        title="The Pragmatic Programmer",
        authors=["Andrew Hunt", "David Thomas"],
        isbn="9780201616224",
        genres=["Programming", "Software Development"],
        publication_year=1999,
        language="English",
        status=ItemStatus.AVAILABLE,
        duration_minutes=540
    )

    # Display created items
    print(ebook)
    print(printed)
    print(paper)
    print(audio)


if __name__ == "__main__":
    main()
