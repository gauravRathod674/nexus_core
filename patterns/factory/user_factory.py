from typing import Type, Dict
from models.users import LibraryUser, Role

class LibraryUserFactory:
    _registered_roles: Dict[str, Role] = {}

    @staticmethod
    def register(role_key: str, role_enum: Role):
        role_key = role_key.lower()
        LibraryUserFactory._registered_roles[role_key] = role_enum

    @staticmethod
    def create(role_key: str, name: str, email: str, password_hash: str) -> LibraryUser:
        role_key = role_key.lower()
        role_enum = LibraryUserFactory._registered_roles.get(role_key)

        if not role_enum:
            raise ValueError(f"User role '{role_key}' is not registered.")

        return LibraryUser(name=name, email=email, password_hash=password_hash, role=role_enum)

def main():
    # Register available roles
    LibraryUserFactory.register("student", Role.STUDENT)
    LibraryUserFactory.register("faculty", Role.FACULTY)
    LibraryUserFactory.register("researcher", Role.RESEARCHER)
    LibraryUserFactory.register("guest", Role.GUEST)
    LibraryUserFactory.register("librarian", Role.LIBRARIAN)

    # Create users using the factory
    alice = LibraryUserFactory.create(
        role_key="faculty",
        name="Alice",
        email="alice@example.com",
        password_hash="hashed123"
    )

    bob = LibraryUserFactory.create(
        role_key="student",
        name="Bob",
        email="bob@example.com",
        password_hash="hashed456"
    )

    # Display created users
    print(alice)
    print(bob)


if __name__ == "__main__":
    main()