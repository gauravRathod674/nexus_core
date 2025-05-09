from enum import Enum, auto
from typing import List

class Role(Enum):
    STUDENT = auto()
    RESEARCHER = auto()
    FACULTY = auto()
    GUEST = auto()
    LIBRARIAN = auto()

class LibraryUser:
    def __init__(self, name: str, email: str, password_hash: str, role: Role):
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.current_loans: List[str] = []  # list of ISBNs

    def can_borrow(self, item_type: str) -> bool:
        if self.role == Role.GUEST:
            return False
        if item_type == "Research Paper" and self.role not in {Role.FACULTY, Role.RESEARCHER}:
            return False
        return True

    def __str__(self):
        return f"{self.name} ({self.role.name})"

     def get_borrow_limit(self) -> int:
        from utils.config import BORROW_LIMITS
        return BORROW_LIMITS.get(self.role, 0)

    def get_borrow_duration(self) -> int:
        from utils.config import BORROW_DURATIONS
        return BORROW_DURATIONS.get(self.role, 0)
