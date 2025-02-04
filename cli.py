import requests

BASE_URL = "syn-q-production.up.railway.app/api"  # Railway URL


def register():
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    org_id = input("Enter your organization ID: ")

    data = {"name": name, "email": email, "password": password, "organization_id": org_id}
    response = requests.post(f"{BASE_URL}/register", json=data)
    print(response.json())


def login():
    email = input("Enter your email: ")
    password = input("Enter your password: ")

    data = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/login", json=data)

    if response.status_code == 200:
        user_data = response.json()["user"]
        print("Login successful!")
        if user_data.get("is_admin", False):
            admin_menu(user_data)
        else:
            print("Welcome, user!")
    else:
        print("Invalid credentials.")


def admin_menu(user_data):
    while True:
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
            print("Logging out...")
            break
        else:
            print("Invalid choice. Try again.")


def view_projects():
    response = requests.get(f"{BASE_URL}/projects")
    print(response.json())


def view_users(org_id):
    response = requests.get(f"{BASE_URL}/organization/{org_id}/users")
    print(response.json())


def main():
    while True:
        print("\nWelcome to Syn-Q CLI")
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
