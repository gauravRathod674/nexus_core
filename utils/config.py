from models.users import Role

# Default limits (# of books) per role
BORROW_LIMITS = {
    Role.STUDENT:    3,
    Role.RESEARCHER: 5,
    Role.FACULTY:    7,
    Role.GUEST:      0,
    Role.LIBRARIAN: 10,
}

# Default durations (days) per role
BORROW_DURATIONS = {
    Role.STUDENT:    14,
    Role.RESEARCHER: 21,
    Role.FACULTY:    30,
    Role.GUEST:      0,
    Role.LIBRARIAN: 60,
}
