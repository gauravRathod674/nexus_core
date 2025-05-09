# utils/search_strategies.py

from abc import ABC, abstractmethod
from typing import List
from models.items import LibraryItem
from utils.dummy_data import get_dummy_items


class SearchStrategy(ABC):
    @abstractmethod
    def search(self, items: List[LibraryItem], query: str) -> List[LibraryItem]:
        """Return the subset of items matching the query."""
        ...


class KeywordSearchStrategy(SearchStrategy):
    """Search for items whose title contains the query (case-insensitive)."""
    def search(self, items: List[LibraryItem], query: str) -> List[LibraryItem]:
        q = query.lower()
        return [item for item in items if q in item.title.lower()]


class AuthorSearchStrategy(SearchStrategy):
    """Search for items by matching author name (case-insensitive)."""
    def search(self, items: List[LibraryItem], query: str) -> List[LibraryItem]:
        q = query.lower()
        return [
            item
            for item in items
            if any(q in author.lower() for author in item.authors)
        ]


class TypeSearchStrategy(SearchStrategy):
    """Search for items by their item_type() string (case-insensitive)."""
    def search(self, items: List[LibraryItem], query: str) -> List[LibraryItem]:
        q = query.lower()
        return [item for item in items if q == item.item_type().lower()]


class GenreSearchStrategy(SearchStrategy):
    """Search for items by genre (case-insensitive, matches any genre tag)."""
    def search(self, items: List[LibraryItem], query: str) -> List[LibraryItem]:
        q = query.lower()
        return [
            item
            for item in items
            if hasattr(item, "genres") and any(q == g.lower() for g in item.genres)
        ]


class SearchContext:
    """Holds a reference to a SearchStrategy and delegates searches to it."""
    def __init__(self, strategy: SearchStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SearchStrategy):
        self._strategy = strategy

    def search(self, items: List[LibraryItem], query: str) -> List[LibraryItem]:
        return self._strategy.search(items, query)


def main():
    items = get_dummy_items()
    context = SearchContext(KeywordSearchStrategy())

    while True:
        print("\nChoose search type:")
        print("  1) Keyword (in title)")
        print("  2) Author")
        print("  3) Item type")
        print("  4) Genre")
        print("  5) Exit")
        choice = input("Enter choice [1-5]: ").strip()

        if choice == "5":
            print("Goodbye!")
            break
        elif choice == "1":
            context.set_strategy(KeywordSearchStrategy())
            prompt = "Enter keyword to search in titles: "
        elif choice == "2":
            context.set_strategy(AuthorSearchStrategy())
            prompt = "Enter author name to search: "
        elif choice == "3":
            context.set_strategy(TypeSearchStrategy())
            prompt = "Enter item type (e.g. E-Book, Printed Book): "
        elif choice == "4":
            context.set_strategy(GenreSearchStrategy())
            prompt = "Enter genre to search (e.g. Fantasy, AI, Python): "
        else:
            print("Invalid choice, please try again.")
            continue

        query = input(prompt).strip()
        results = context.search(items, query)

        print(f"\nResults ({len(results)} found):")
        if results:
            for it in results:
                print(f"  • {it}")
        else:
            print("  No items match your query.")


if __name__ == "__main__":
    main()
