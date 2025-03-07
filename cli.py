import requests
import os
import jwt

# Define public URLs for each microservice (replace with actual public URLs)
AUTH_URL = "https://syn-q-authservice-production.up.railway.app"  # URL for auth service
PROJECT_URL = "https://syn-q-projectservice-production.up.railway.app"  # URL for project service
QUEUE_URL = "https://syn-q-queue-service-production.up.railway.app"  # URL for queue service
NOTIFICATION_URL = "https://web-production-d1ba5.up.railway.app"  # URL for notification service

# Global variables to store JWT token, organization ID, user_id (from login)
jwt_token = None
organization_id = None
user_id = None
is_admin = False

# Registration Function
def register():
    print("Register a new user:")

    name = input("Enter your name: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    org_id = input("Enter your organization ID: ")
    org_passcode = input("Enter your organization passcode: ")

    data = {
        "name": name,
        "email": email,
        "password": password,
        "organization_id": org_id,
        "org_passcode": org_passcode
    }

    response = requests.post(f"{AUTH_URL}/register", json=data)

    if response.status_code == 201:
        print("Registration successful!")
    else:
        print(f"Error: {response.json()['message']}")

# Login Function
def login():
    global jwt_token, organization_id, user_id, is_admin

    print("Login:")

    email = input("Enter your email: ")
    password = input("Enter your password: ")

    data = {"email": email, "password": password}
    response = requests.post(f"{AUTH_URL}/login", json=data)

    print("Response status:", response.status_code)
    print("Response JSON:", response.json())

    if response.status_code == 200:
        jwt_token = response.json().get("token")

        if jwt_token:
            print("Login successful!")

            # Decode the JWT token to extract organization_id, user_id, and is_admin
            try:
                decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})  # Decode without verifying signature (for testing purposes)
                print("Decoded Token:", decoded_token)  # Debugging line

                organization_id = decoded_token.get("org_id")
                user_id = decoded_token.get("user_id")  # Extract the user_id
                is_admin = decoded_token.get("is_admin", False)  # Get admin status from the token

                if organization_id and user_id is not None:
                    print(f"Organization ID: {organization_id} extracted from token.")
                    print(f"User ID: {user_id} extracted from token.")
                    return jwt_token
                else:
                    print("Error: Missing user information (organization or user_id) in token.")
                    return None
            except Exception as e:
                print(f"Error decoding token: {e}")
                return None
        else:
            print("Error: Missing 'token' in response.")
            return None
    else:
        print(f"Error: {response.json().get('message', 'Unknown error')}")
        return None


# Add a new project
def add_project():
    print("Add a new project:")

    project_number = input("Enter project number: ").strip()
    client_name = input("Enter client name: ").strip()
    project_name = input("Enter project name: ").strip()

    headers = {
        "Authorization": f"Bearer {jwt_token}"  # Ensure the token is passed here
    }

    data = {
        "project_number": project_number,
        "client_name": client_name,
        "project_name": project_name,
        "organization_id": organization_id  # Ensure organization_id is passed as part of the project data
    }

    # Call the API to add the project
    url = f"{PROJECT_URL}/projects"

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"Project '{project_name}' added successfully!")
    else:
        print(f"Error: {response.status_code} - {response.text}")


# Add a new project file
def add_project_file():
    print("Add a new project file:")

    project_number = input("Enter project number: ")

    # Initialize an empty list to hold files
    files_data = []

    while True:
        file_name = input("Enter file name: ")
        file_type = input("Enter file type: ")

        # Append the new file details to the list
        files_data.append({
            "file_name": file_name,
            "file_type": file_type
        })

        # Ask if the user wants to add more files
        more_files = input("Do you want to add another file? (y/n): ").strip().lower()
        if more_files != 'y':
            break  # Exit the loop if the user doesn't want to add more files

    headers = {
        "Authorization": f"Bearer {jwt_token}"  # Ensure the token is passed here
    }

    # Make the POST request to add the project files
    response = requests.post(f"{PROJECT_URL}/projects/{project_number}/files", headers=headers, json=files_data)

    if response.status_code == 201:
        print(f"{len(files_data)} Project file(s) added successfully!")
    else:
        print(f"Error: {response.json()['message']}")


# Sync project files with MongoDB QueueService
def sync_project_files_with_mongo():
    print("Syncing project files with MongoDB...")

    response = requests.post(f"{PROJECT_URL}/sync-files", headers={"Authorization": f"Bearer {jwt_token}"})

    if response.status_code == 200:
        print("Project files synced successfully!")
    else:
        print(f"Error: {response.json()['message']}")

# View Projects Function
def get_projects():
    print("Fetching your projects...")

    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    url = f"{PROJECT_URL}/projects/organization/{organization_id}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        projects = response.json().get("projects", [])

        if not projects:
            print("No projects found for this organization.")
            return

        print("\n--- Projects List ---")
        for i, proj in enumerate(projects):
            print(f"{i+1}. Project Number: {proj['project_number']} | Client: {proj['client_name']}")

        project_choice = int(input("\nSelect a project by number: "))
        if 1 <= project_choice <= len(projects):
            selected_project = projects[project_choice - 1]
            get_project_files(selected_project)  # Show files for the selected project
        else:
            print("Invalid project choice.")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Get Project Files Function
def get_project_files(project):
    print(f"Fetching files for Project {project['project_number']}...")

    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    url = f"{PROJECT_URL}/projects/{project['project_number']}/files"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        files = response.json().get("files", [])
        if not files:
            print("No files found for this project.")
            return

        print("\n--- Files List ---")
        for i, file in enumerate(files):
            print(f"{i+1}. {file['file_name']} (Type: {file['file_type']})")

        file_choice = int(input("\nSelect a file by number to view: "))
        if 1 <= file_choice <= len(files):
            selected_file = files[file_choice - 1]
            print(f"Selected file: {selected_file['file_name']}")
            # Prompt user to join queue
            join_queue_choice = input("Do you want to join the queue for this file? (y/n): ").strip().lower()
            if join_queue_choice == 'y':
                join_queue(selected_file)
            else:
                print("Returning to project files.")
        else:
            print("Invalid file choice.")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Join Queue Function
def join_queue(file):
    print(f"Joining queue for file {file['file_name']}...")

    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    data = {
        "user_id": user_id,  # Use the user_id extracted from the JWT token
        "project_file": file['file_name']
    }

    response = requests.post(f"{QUEUE_URL}/join-queue", json=data, headers=headers)

    if response.status_code == 200:
        print(f"Successfully joined the queue for {file['file_name']}.")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# View My Queues Function
def get_my_queues():
    print("Fetching your queues...")

    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    url = f"{QUEUE_URL}/my-queues?user_id={user_id}"  # Pass user_id as query parameter

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        queues = response.json().get("queues", [])
        if not queues:
            print("You are not currently in any queues.")
            return

        print("\n--- Your Queues ---")
        for queue in queues:
            print(f"Queue ID: {queue['id']} | Project File: {queue['project_file']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


# View all projects in the organization (Admin only)
def view_organization_projects(organization_id):
    print("Fetching organization projects...")

    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    url = f"{PROJECT_URL}/projects/organization/{organization_id}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        projects = response.json().get("projects", [])

        if not projects:
            print("No projects found for this organization.")
            return

        print("\n--- Organization Projects ---")
        for i, project in enumerate(projects):
            print(f"{i+1}. Project Number: {project['project_number']} | Client: {project['client_name']}")

    else:
        print(f"Error: {response.status_code} - {response.text}")

# View all users in the organization (Admin only)
def view_all_users():
    print("Fetching all users in your organization...")

    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    url = f"{AUTH_URL}/users/organization/{organization_id}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        users = response.json().get("users", [])

        if not users:
            print("No users found in your organization.")
            return

        print("\n--- Users List ---")
        for i, user in enumerate(users):
            print(f"{i+1}. {user['name']} | {user['email']}")

    else:
        print(f"Error: {response.status_code} - {response.text}")


# View all project files (Admin only)
# CLI: view_all_files()
def view_all_files():
    print("Fetching all project files in your organization...")

    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    # Make a request to get all files across all projects in the organization
    url = f"{PROJECT_URL}/files/organization/{organization_id}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        files = response.json().get("files", [])

        if not files:
            print("No files found for your projects.")
            return

        print("\n--- All Files ---")
        for i, file in enumerate(files):
            print(f"{i+1}. {file['file_name']} (Type: {file['file_type']})")

    else:
        print(f"Error: {response.status_code} - {response.text}")



# Main CLI Function
def main():
    print("Welcome to Syn-Q CLI")
    jwt_token = None
    organization_id = None
    user_id = None
    is_admin = False

    while True:
        if not jwt_token:
            # If not logged in, show login/register options
            print("1. Register")
            print("2. Login")
            choice = input("Enter your choice: ").strip()

            if choice == '1':
                register()
            elif choice == '2':
                jwt_token = login()
                if jwt_token:
                    print("You are logged in!")

                    # After login, decode the token to extract user details
                    decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
                    organization_id = decoded_token.get("org_id")
                    user_id = decoded_token.get("user_id")
                    is_admin = decoded_token.get("is_admin", False)

                    print(f"Organization ID: {organization_id} extracted from token.")
                    print(f"User ID: {user_id} extracted from token.")
                    print(f"Admin Status: {is_admin}")
                else:
                    print("Login failed. Please try again.")
        else:
            # If logged in, show the main menu
            print(f"Logged in! Welcome back.")

            if is_admin:
                # Show Admin options
                print("\nAdmin Options:")
                print("1. View Organization Projects")
                print("2. View All Users")
                print("3. View All Files")
                print("4. Add Project")
                print("5. Add Project File")
                print("6. Sync Project Files with MongoDB")
                print("7. Log Out")
                admin_choice = input("Enter your choice: ").strip()

                if admin_choice == "1":
                    view_organization_projects(organization_id)
                elif admin_choice == "2":
                    view_all_users()
                elif admin_choice == "3":
                    view_all_files()
                elif admin_choice == "4":
                    add_project()
                elif admin_choice == "5":
                    add_project_file()
                elif admin_choice == "6":
                    sync_project_files_with_mongo()
                elif admin_choice == "7":
                    print("Logging out...")
                    jwt_token = None
                    organization_id = None
                    user_id = None
                    is_admin = False
                else:
                    print("Invalid choice. Returning to the main menu.")
            else:
                # Show User options
                print("\n1. View Projects")
                print("2. View My Queues")
                print("3. Logout")
                user_choice = input("Enter your choice: ").strip()

                if user_choice == "1":
                    get_projects()  # No need to pass organization_id, it’s globally set
                elif user_choice == "2":
                    get_my_queues()  # No need to pass user_id, it’s globally set
                elif user_choice == "3":
                    print("Logging out...")
                    jwt_token = None
                    organization_id = None
                    user_id = None
                    is_admin = False
                else:
                    print("Invalid choice. Returning to the main menu.")


if __name__ == "__main__":
    main()
