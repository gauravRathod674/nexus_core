    from models.users import LibraryUser, Role

    def show_menu():
        print("\nWelcome to Nexus Library System!")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Please select an option (1/2/3): ")
        return choice

    def register_user(users_db):
        print("\nRegistration")
        name = input("Enter name: ")
        email = input("Enter email: ")
        password = input("Enter password: ")
        
        # User role selection
        print("Select role:")
        for role in Role:
            print(f"{role.value}. {role.name}")
        role_choice = int(input("Enter role number: "))
        
        role = Role(role_choice)  
        user = LibraryUser(name, email, password, role)
        
        users_db[email] = user  # Store user in the mock database
        print(f"Registration successful for {name} ({role.name})")

    def login_user(users_db):
        print("\nLogin")
        email = input("Enter email: ")
        password = input("Enter password: ")

        # Check if the user exists and password matches
        user = users_db.get(email)
        if user and user.password_hash == password:
            print(f"Login successful! Welcome, {user.name} ({user.role.name})")
            return user
        else:
            print("Invalid email or password. Please try again.")
            return None

    def main():
        users_db = {}  # Mock database (could be replaced with actual database in future)
        
        while True:
            choice = show_menu()
            
            if choice == '1':  # Register user
                register_user(users_db)
            elif choice == '2':  # Login user
                user = login_user(users_db)
                if user:
                    # After login, show menu based on user role
                    if user.role == Role.STUDENT:
                        print("\nStudent Menu: Borrow books, View borrowed items")
                    elif user.role == Role.FACULTY:
                        print("\nFaculty Menu: Borrow books, Add new books, View borrowed items")
                    # Add more role-based functionalities as needed
            elif choice == '3':  # Exit
                print("Exiting... Goodbye!")
                break
            else:
                print("Invalid option, please try again.")

    if __name__ == "__main__":
        main()