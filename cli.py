import requests

BASE_URL = "https://syn-q-production.up.railway.app/api"  # Railway URL


def register():
    print("\nBefore registering, please make sure to have your organization credentials available.")
    print("Registration will take less than 5 minutes. Please enter the required information below.")

    # Ask if registering as a User or Admin
    while True:
        user_type = input("Are you registering as a (1) Regular User or (2) Admin? Enter 1 or 2: ").strip()
        if user_type in ["1", "2"]:
            break
        print("Invalid choice. Please enter 1 for User or 2 for Admin.")

    name = input("Enter your name: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    org_id = input("Enter your organization ID: ")
    org_passcode = input("Enter the organization passcode: ")  # New field
    is_admin = False        # Defaults to false

    # Determine if user is an admin
    if user_type == "2":
        is_admin = True

    data = {
        "name": name,
        "email": email,
        "password": password,
        "organization_id": org_id,
        "org_passcode": org_passcode,
        "is_admin": is_admin  # Include admin flag
    }

    response = requests.post(f"{BASE_URL}/register", json=data)

    if response.status_code == 201:
        if is_admin:
            print("Admin registered successfully! You can now manage projects and users in your organization.")
        else:
            print("User registered successfully! Now you can join project queues in your organization!")
    else:
        print(f"Error: 'Registration failed. Please try again.'")


def login():
    email = input("Enter your email: ")
    password = input("Enter your password: ")

    data = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/login", json=data)

    if response.status_code == 200:
        user_data = response.json()["user"]

        print("Login successful!")

        # print(f"DEBUG: user_data received → {user_data}")  # Debugging line

        if user_data.get("is_admin", False): # Ensure it defaults to False if missing
            admin_menu(user_data)
        else:
            # print("Welcome, user!")
            user_menu(user_data)  # Regular user menu
    else:
        print("Invalid credentials.")


def admin_menu(user_data):
    while True:
        print(f"Welcome, {user_data['name']}!")
        print("\nAdmin Menu:")
        print("1. View all projects")
        print("2. View all users in organization")
        print("3. Logout")
        choice = input("Enter your choice: ")

        if choice == "1":
            view_projects()
        elif choice == "2":
            view_users(user_data["organization_id"])
        elif choice == "3":
            confirm = input("Are you sure you want to log out? If you log out, you will lose all "
                            "unsaved work. (y/n): ").strip().lower()
            if confirm == "y":
                print("Logging out...")
                break
            else:
                print("Logout canceled.")
        else:
            print("Invalid choice. Try again.")


def user_menu(user_data):
    while True:
        print(f"Welcome, {user_data['name']}!")
        print("\nUser Menu:")
        print("1. View all projects")  # Users can still see projects
        print("2. Logout")
        choice = input("Enter your choice: ")

        if choice == "1":
            view_projects()
        elif choice == "2":
            confirm = input("Are you sure you want to log out? If you log out, you are relinquishing your "
                            "spot in the queues you have joined. (y/n): ").strip().lower()
            if confirm == "y":
                print("Logging out...")
                break
            else:
                print("Logout canceled.")
        else:
            print("Invalid choice. Try again.")


def view_projects():
    print("\nSelect project view:")
    print("1. Summary List")
    print("2. Detailed View (Includes Files)")

    choice = input("Enter your choice (1 or 2): ").strip()

    response = requests.get(f"{BASE_URL}/projects")
    projects = response.json().get("projects", [])

    if not projects:
        print("No projects found.")
        return

    if choice == "1":
        print("\n--- Project List ---")
        for proj in projects:
            print(f"Project Number: {proj['project_number']} | Client: {proj['client_name']}")
        print("-" * 30)

    elif choice == "2":
        print("\n--- Project Details ---")
        for proj in projects:
            print(f"Project Number: {proj['project_number']}")
            print(f"Client Name: {proj['client_name']}")
            print("Files:")
            for file in proj["files"]:
                print(f"  - {file['file_name']} ({file['file_type']})")
            print("-" * 30)
    else:
        print("Invalid choice. Defaulting to Summary List.")
        view_projects()


def view_users(org_id):
    print("\nUser Search Options:")
    print("1. View all users")
    print("2. Search by name")
    print("3. Search by email")

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        response = requests.get(f"{BASE_URL}/organization/{org_id}/users")
    elif choice == "2":
        search_name = input("Enter name to search: ").strip()
        response = requests.get(f"{BASE_URL}/organization/{org_id}/users?name={search_name}")
    elif choice == "3":
        search_email = input("Enter email to search: ").strip()
        response = requests.get(f"{BASE_URL}/organization/{org_id}/users?email={search_email}")
    else:
        print("Invalid choice. Defaulting to all users.")
        response = requests.get(f"{BASE_URL}/organization/{org_id}/users")

    if response.status_code == 200:
        users = response.json().get("users", [])
        if not users:
            print("No users found.")
        else:
            print("\n--- Users in Organization ---")
            for user in users:
                print(f"User ID: {user['id']}, Name: {user['name']}, Email: {user['email']}, Admin: {user['is_admin']}")
            print("-" * 30)
    else:
        print("Error fetching users.")


def main():
    while True:
        print("\nWelcome to Syn-Q CLI!")
        print("\nRegister or login to begin joining project queues!")

        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
