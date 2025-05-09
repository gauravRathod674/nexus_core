from abc import ABC, abstractmethod
from models.items import LibraryItem
from models.users import LibraryUser

class ItemState(ABC):
    """Base for all item states."""

    @abstractmethod
    def borrow(self, item: LibraryItem, user: LibraryUser) -> (bool, str):
        pass

    @abstractmethod
    def return_item(self, item: LibraryItem, user: LibraryUser) -> (bool, str):
        pass

    @abstractmethod
    def reserve(self, item: LibraryItem, user: LibraryUser) -> (bool, str):
        pass
