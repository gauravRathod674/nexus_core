from abc import ABC, abstractmethod
from typing import List
from models.items import LibraryItem
from utils.dummy_data import get_dummy_items


class SearchStrategy(ABC):
    @abstractmethod
    def search(self, items: List[LibraryItem], query: str) -> List[LibraryItem]:
        """Return the subset of items matching the query."""
        pass


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

    print("=== Keyword Search: 'deep' ===")
    for it in context.search(items, "deep"):
        print(f"  • {it}")

    print("\n=== Author Search: 'Orwell' ===")
    context.set_strategy(AuthorSearchStrategy())
    for it in context.search(items, "Orwell"):
        print(f"  • {it}")

    print("\n=== Type Search: 'research paper' ===")
    context.set_strategy(TypeSearchStrategy())
    for it in context.search(items, "Research Paper"):
        print(f"  • {it}")


if __name__ == "__main__":
    main()