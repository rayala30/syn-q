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
    print("---------------------Register New User---------------------")

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

    print("---------------------Login---------------------")

    email = input("Enter your email: ")
    password = input("Enter your password: ")

    data = {"email": email, "password": password}
    response = requests.post(f"{AUTH_URL}/login", json=data)

    # Debug line
    # print("Response status:", response.status_code)
    # print("Response JSON:", response.json())

    if response.status_code == 200:
        jwt_token = response.json().get("token")

        if jwt_token:
            print("Login successful!")

            # Decode the JWT token to extract organization_id, user_id, and is_admin
            try:
                decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})  # Decode without verifying signature (for testing purposes)
                # print("Decoded Token:", decoded_token)  # Debugging line

                organization_id = decoded_token.get("org_id")
                user_id = decoded_token.get("user_id")  # Extract the user_id
                is_admin = decoded_token.get("is_admin", False)  # Get admin status from the token

                if organization_id and user_id is not None:
                    # Debugging
                    print(f"Your Organization ID: {organization_id}")
                    print(f"Your User ID: {user_id}")
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
    print("---------------------Add Project---------------------")

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
    print("---------------------Add Project File---------------------")

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


def get_projects_from_postgres():

    print("\nFetching projects from Postgres...")

    headers = {"Authorization": f"Bearer {jwt_token}"}  # Pass the JWT token for authorization
    response = requests.get(f"{PROJECT_URL}/projects/organization/{organization_id}", headers=headers)

    if response.status_code == 200:
        projects = response.json()["projects"]
        return projects  # Return list of projects
    else:
        print(f"Error fetching projects: {response.status_code} - {response.text}")
        return []


def get_project_files_from_postgres(project_number):
    print(f"\nFetching project files for Project {project_number}...")

    headers = {"Authorization": f"Bearer {jwt_token}"}  # Pass the JWT token for authorization
    response = requests.get(f"{PROJECT_URL}/projects/{project_number}/files", headers=headers)

    if response.status_code == 200:
        files = response.json()["files"]
        return files  # Return list of files for the given project
    else:
        print(f"Error fetching files for project {project_number}: {response.status_code} - {response.text}")
        return []


# Sync project files with MongoDB QueueService
def sync_project_files_with_mongo():
    print("\nSyncing project files with MongoDB...")

    headers = {"Authorization": f"Bearer {jwt_token}"}  # Pass JWT token for auth

    # Get the list of projects for the organization
    projects = get_projects_from_postgres()

    if not projects:
        print("No projects found!")
        return

    # Loop through each project and sync its files with MongoDB
    for project in projects:
        project_number = project["project_number"]
        print(f"Syncing files for project {project_number}...")

        # Get the project files for this project
        files = get_project_files_from_postgres(project_number)

        if not files:
            print(f"No files found for project {project_number}!")
            continue

        # Prepare the list of files to be added, checking for duplicates
        files_data = []
        for file in files:
            files_data.append({
                "file_name": file["file_name"],
                "file_type": file["file_type"],
                "file_queue": []
            })

        # Check if the project already has these files before syncing
        response = requests.post(f"{QUEUE_URL}/sync-project-files", headers=headers, json={
            "project_number": project_number,
            "org_id": organization_id,
            "files": files_data  # Insert all files for this project in one array
        })

        if response.status_code == 200:
            print(f"Successfully synced files for project {project_number} to MongoDB.")
        else:
            print(f"Error syncing project {project_number}: {response.status_code} - {response.text}")


# View Projects Function
def get_projects():
    print("Fetching your projects...")

    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{PROJECT_URL}/projects/organization/{organization_id}", headers=headers)

    if response.status_code == 200:
        projects = response.json().get("projects", [])
        if not projects:
            print("No projects found for your organization.")
            return

        print("\n---------------------Projects List---------------------")
        for idx, project in enumerate(projects, 1):
            print(f"{idx}. Project Number: {project['project_number']} | Client: {project['client_name']}")

        try:
            selected_project = input("\nSelect a project by number or press 'b' to go back: ").strip()

            if selected_project.lower() == 'b':  # Allow the user to go back
                print("Going back to the previous menu.")
                return

            selected_project = int(selected_project) - 1  # Convert to 0-based index
            if selected_project < 0 or selected_project >= len(projects):
                print("Invalid project selection. Please select a valid number.")
                return

            project_number = projects[selected_project]["project_number"]

            # Fetch files for the selected project
            get_project_files(project_number)  # Pass project_number here

        except ValueError:
            print("Invalid input. Please enter a valid project number or 'b' to go back.")

    else:
        print(f"Error: {response.json().get('message', 'Unknown error occurred.')}")


# Get Project Files Function
def get_project_files(project_number):
    print(f"\nFetching files for Project {project_number}...")

    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{PROJECT_URL}/projects/{project_number}/files", headers=headers)

    if response.status_code == 200:
        files = response.json().get("files", [])
        if not files:
            print(f"No files found for Project {project_number}.")
            return

        print("\n---------------------Files List---------------------")
        for idx, file in enumerate(files, 1):
            print(f"{idx}. {file['file_name']} (Type: {file['file_type']})")

        # Prompt user to select a file or go back
        selected_file = input("\nSelect a file by number to view, or press 'b' to go back: ").strip()

        if selected_file.lower() == 'b':  # Allow the user to go back
            print("Going back to the previous menu.")
            return

        try:
            selected_file = int(selected_file) - 1  # Convert to 0-based index
            if selected_file < 0 or selected_file >= len(files):
                print("Invalid file selection. Please select a valid number.")
                return

            selected_file_details = files[selected_file]

            # Ask user if they want to join the queue for the file
            join_file = input(
                f"Do you want to join the queue for file {selected_file_details['file_name']}? (y/n): ").strip().lower()

            if join_file == "y":
                join_queue(selected_file_details, project_number)  # Pass both file details and project_number

        except ValueError:
            print("Invalid input. Please enter a valid file number or 'b' to go back.")

    else:
        print(f"Error: {response.json().get('message', 'Unknown error occurred.')}")
        return


# Join Queue Function
def join_queue(selected_file_details, project_number):
    print(f"\nJoining queue for file {selected_file_details['file_name']}...")

    headers = {"Authorization": f"Bearer {jwt_token}"}
    data = {
        "user_id": user_id,  # Ensure this is correctly set from your current session
        "project_number": project_number,
        "file_name": selected_file_details['file_name'],
        "file_type": selected_file_details['file_type']
    }

    response = requests.post(f"{QUEUE_URL}/join-file-queue", headers=headers, json=data)

    if response.status_code == 200:
        print(f"Successfully joined the queue for {selected_file_details['file_name']}.")
    else:
        # Print the full response content for debugging
        # print(f"Error: {response.status_code} - {response.text}")
        try:
            print(f"Error: {response.json()['message']}")
        except KeyError:
            print("Error: The response did not contain a 'message' key.")


# Function to get all users in the organization
def get_users_in_organization(organization_id):
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    # Fetch all users from the auth service
    response = requests.get(f"{AUTH_URL}/users/organization/{organization_id}", headers=headers)

    if response.status_code == 200:
        users = response.json().get("users", [])
        return {user['id']: user['name'] for user in users}  # Map user_id to user email
    else:
        print(f"Error fetching users: {response.status_code} - {response.text}")
        return {}


def handle_queue_action(queue, selected_file, action):
    """
    Handle actions like 'Complete Sync', 'Leave Queue', or 'Back'.
    """
    file_queue = selected_file.get('file_queue', [])

    if action == "complete_sync":
        # Check if user is the first in the queue
        if file_queue and file_queue[0] == user_id:
            print("You are the first in the queue.")
            user_choice = input("Do you want to mark this file as 'Completed Sync'? (y/n): ").strip().lower()
            if user_choice == "y":
                # Proceed with completing the sync
                print(f"Sync completed for file: {selected_file['file_name']}.")

                # Send the sync completed request to the backend
                response = requests.post(
                    f"{QUEUE_URL}/complete-sync",
                    json={
                        "project_number": queue["project_number"],
                        "file_name": selected_file["file_name"]
                    }
                )
                if response.status_code == 200:
                    print(f"Successfully marked {selected_file['file_name']} as completed in the queue.")
                    # Automatically remove the user from the queue after completing sync
                    remove_from_queue(selected_file, queue)
                else:
                    print(f"Error marking sync as completed: {response.text}")
            else:
                print("Sync not completed.")
        else:
            print("It is not your turn to sync yet!")

    elif action == "leave_queue":
        remove_from_queue(selected_file, queue)

    elif action == "back":
        print("Going back to the previous menu.")
        return
    else:
        print("Invalid choice. Please select again.")


def remove_from_queue(selected_file, queue):
    """
    Removes the user from the file's queue.
    """
    file_queue = selected_file['file_queue']

    if user_id in file_queue:
        file_queue.remove(user_id)
        print(f"\nYou have left the queue for file {selected_file['file_name']}.")

        # Update the MongoDB queue document
        response = requests.post(
            f"{QUEUE_URL}/update-queue",
            json={
                "project_number": queue["project_number"],
                "file_name": selected_file["file_name"],
                "file_queue": file_queue  # Remove user from the queue
            }
        )
        if response.status_code == 200:
            print(f"Successfully removed you from the queue for {selected_file['file_name']}.")
        else:
            print(f"Error removing from queue: {response.text}")
    else:
        print("You are not in the queue for this file.")


# Function to view user's active queues
def view_my_queues():
    print("Fetching your queues...")

    # Get the organization ID and user ID from the logged-in user
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    # Send request to the Queue service, passing user_id in the URL
    response = requests.get(f"{QUEUE_URL}/my-queues/{user_id}", headers=headers)

    if response.status_code == 200:
        queues = response.json().get("activeQueues", [])
        if not queues:
            print("You are not in any active queues.")
            return

        # Get the list of users in the organization for mapping user_id to names
        users = get_users_in_organization(organization_id)

        print("\n---------------------Active Queues---------------------")
        file_counter = 1  # Start numbering from 1 for all files

        files_list = []  # Create a list to keep track of all the files

        for queue in queues:
            print(f"Project Number: {queue['project_number']}")
            for file in queue['files']:
                file_users = [users.get(user_id, f"User-{user_id}") for user_id in file['file_queue']]
                print(f"{file_counter}. File: {file['file_name']} (Type: {file['file_type']})")
                print(f"   Queue: {', '.join(file_users)}")
                files_list.append((file, queue))  # Add the file and its queue to the list
                file_counter += 1  # Increment the counter for the next file

        # Option for the user to select a queue to edit or go back
        selected_file_number = input("\nSelect which file to edit (enter number) or press 'b' to go back: ").strip()

        if selected_file_number.lower() == 'b':  # Check if user wants to go back
            print("Going back to the previous menu.")
            return  # Exit the function and go back to the main menu

        # Proceed with selecting the file
        try:
            selected_file_number = int(selected_file_number) - 1
            if selected_file_number >= 0 and selected_file_number < len(files_list):
                selected_file, selected_queue = files_list[selected_file_number]  # Get the selected file and its queue

                # If a valid file is selected, proceed with the next actions
                print(f"\nSelected file: {selected_file['file_name']}")
                print("Choose an action:")
                print("1. Complete Sync (if it's your turn in the queue)")
                print("2. Leave Queue")
                print("3. Back")

                action_choice = input("\nEnter your choice: ").strip()

                # Call the handle_queue_action function based on the user's choice
                if action_choice == "1":
                    handle_queue_action(selected_queue, selected_file, "complete_sync")
                elif action_choice == "2":
                    handle_queue_action(selected_queue, selected_file, "leave_queue")
                elif action_choice == "3":
                    print("Going back to the previous menu.")
                    return  # Go back to the previous menu
                else:
                    print("Invalid choice.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please enter a valid number or 'b' to go back.")
    else:
        print(f"Error: {response.status_code} - {response.text}")


# View all projects in the organization (Admin only)
def view_organization_projects(organization_id):
    print("\nFetching organization projects...")

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

        print("\n---------------------Organization Projects---------------------")
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

        print("---------------------User List---------------------")

        for i, user in enumerate(users):
            print(f"{i+1}. {user['name']} | {user['email']}")

    else:
        print(f"Error: {response.status_code} - {response.text}")


# View all project files (Admin only)
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

        print("\n---------------------All Project Files---------------------")
        for i, file in enumerate(files):
            print(f"{i+1}. {file['file_name']} (Type: {file['file_type']})")

    else:
        print(f"Error: {response.status_code} - {response.text}")


# View active queues (Admin only)
def view_active_queues():
    print("Fetching active queues...")

    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    url = f"{QUEUE_URL}/active-queues"  # Endpoint to fetch active queues

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        active_queues = response.json().get("active_queues", [])

        if not active_queues:
            print("No active queues found.")
            return

        # Get the list of users in the organization for mapping user_id to names
        users = get_users_in_organization(organization_id)

        print("\n---------------------All Active Queues---------------------")
        file_counter = 1  # Start numbering from 1 for all files

        for queue in active_queues:
            print(f"Project Number: {queue['project_number']}")
            for file in queue['active_files']:
                # Convert user IDs to user names
                file_users = [users.get(user_id, f"User-{user_id}") for user_id in file['file_queue']]
                print(f"{file_counter}. File: {file['file_name']} (Type: {file['file_type']})")
                print(f"   Queue: {', '.join(file_users)}")
                file_counter += 1  # Increment the counter for the next file

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
            print("\n-------------------------SYN-Q MAIN MENU-------------------------")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Enter your choice: ").strip()

            if choice == '1':
                register()
            elif choice == '2':
                jwt_token = login()
                if jwt_token:
                    print("Hello!")

                    # After login, decode the token to extract user details
                    decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
                    organization_id = decoded_token.get("org_id")
                    user_id = decoded_token.get("user_id")
                    is_admin = decoded_token.get("is_admin", False)

                    # DEBUG STATEMENTS
                    # print(f"Organization ID: {organization_id} extracted from token.")
                    # print(f"User ID: {user_id} extracted from token.")
                    # print(f"Admin Status: {is_admin}")
                else:
                    print("Login failed. Please try again.")
            elif choice == '3':
                print("Thank you for using Syn-Q!")
                break
        else:
            # If logged in, show the main menu
            # print(f"Logged in! Welcome back.")

            if is_admin:
                # Show Admin options
                print("\nAdmin Options:")
                print("1. View Organization Projects")
                print("2. View All Users")
                print("3. View All Files")
                print("4. View Active Queues")  # New option for active queues
                print("5. Add Project")
                print("6. Add Project File")
                print("7. Sync Project Files with MongoDB")
                print("8. Log Out")
                admin_choice = input("Enter your choice: ").strip()

                if admin_choice == "1":
                    view_organization_projects(organization_id)
                elif admin_choice == "2":
                    view_all_users()
                elif admin_choice == "3":
                    view_all_files()
                elif admin_choice == "4":
                    view_active_queues()  # Call the new function to view active queues
                elif admin_choice == "5":
                    add_project()
                elif admin_choice == "6":
                    add_project_file()
                elif admin_choice == "7":
                    sync_project_files_with_mongo()
                elif admin_choice == "8":
                    print("Logging out...")
                    jwt_token = None
                    organization_id = None
                    user_id = None
                    is_admin = False
                else:
                    print("Invalid choice. Returning to the main menu.")

            else:
                # Show User options
                print("\nUser Options:")
                print("1. View Projects")
                print("2. View My Queues")
                print("3. Logout")
                user_choice = input("Enter your choice: ").strip()

                if user_choice == "1":
                    get_projects()  # No need to pass organization_id, it’s globally set
                elif user_choice == "2":
                    view_my_queues()  # No need to pass user_id, it’s globally set
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
