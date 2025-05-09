from abc import ABC, abstractmethod
from typing import List, Dict
from models.users import LibraryUser
from models.items import LibraryItem
from utils.dummy_data import get_dummy_transactions, get_dummy_items, get_dummy_reservations, get_dummy_users


class RecommendationStrategy(ABC):
    @abstractmethod
    def recommend(self, user: LibraryUser, items: List[LibraryItem]) -> List[LibraryItem]:
        pass


class HistoryBasedRecommendation(RecommendationStrategy):
    def __init__(self, user_transactions: List):
        self.user_transactions = user_transactions

    def recommend(self, user: LibraryUser, items: List[LibraryItem]) -> List[LibraryItem]:
        past_isbns = [
            tx.isbn for tx in self.user_transactions if tx.user_name == user.name
        ]
        genre_counts = {}
        for item in items:
            if item.isbn in past_isbns:
                for genre in getattr(item, "genres", []):
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1

        if not genre_counts:
            return []

        scored = []
        for item in items:
            if item.isbn in past_isbns:
                continue
            score = sum(genre_counts.get(genre, 0) for genre in getattr(item, "genres", []))
            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:5]]


class TrendingRecommendation(RecommendationStrategy):
    def __init__(self, transactions, reservations):
        self.transactions = transactions
        self.reservations = reservations

    def recommend(self, user: LibraryUser, items: List[LibraryItem]) -> List[LibraryItem]:
        usage_counts: Dict[str, int] = {}
        for tx in self.transactions:
            usage_counts[tx.isbn] = usage_counts.get(tx.isbn, 0) + 1
        for res in self.reservations:
            usage_counts[res.isbn] = usage_counts.get(res.isbn, 0) + 1

        scored = [
            (usage_counts.get(item.isbn, 0), item)
            for item in items if usage_counts.get(item.isbn, 0) > 0
        ]

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:5]]


class RecommendationEngine:
    def __init__(self, strategy: RecommendationStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: RecommendationStrategy):
        self._strategy = strategy

    def recommend(self, user: LibraryUser, items: List[LibraryItem]) -> List[LibraryItem]:
        return self._strategy.recommend(user, items)


def main():
    users = get_dummy_users()
    items = get_dummy_items()
    txs = get_dummy_transactions()
    reservations = get_dummy_reservations()

    print("\n Select a user to get recommendations:")
    for idx, user in enumerate(users):
        print(f"{idx + 1}) {user.name} ({user.role.name})")

    choice = input("\nEnter user number: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(users)):
        print(" Invalid selection.")
        return

    user = users[int(choice) - 1]
    print(f"\n Recommendations for {user.name} ({user.role.name}):\n")

    engine = RecommendationEngine(HistoryBasedRecommendation(txs))
    print(" Based on Borrowing History:")
    for item in engine.recommend(user, items):
        print(f" - {item.title} ({item.isbn})")

    engine.set_strategy(TrendingRecommendation(txs, reservations))
    print("\n Based on Trending Usage:")
    for item in engine.recommend(user, items):
        print(f" - {item.title} ({item.isbn})")


if __name__ == "__main__":
    main()
