import requests
import os
import jwt  # Import the JWT decoding library

# Define public URLs for each microservice (replace with actual public URLs)
AUTH_URL = "https://syn-q-authservice-production.up.railway.app"  # URL for auth service
PROJECT_URL = "https://syn-q-projectservice-production.up.railway.app"  # URL for project service
QUEUE_URL = "https://syn-q-queue-service-production.up.railway.app"  # URL for queue service
NOTIFICATION_URL = "https://web-production-d1ba5.up.railway.app"  # URL for notification service


# Global variables to store JWT token and organization ID (from login)
jwt_token = None
organization_id = None

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
    global jwt_token, organization_id  # Use global variables to store the token and organization_id

    print("Login:")

    email = input("Enter your email: ")
    password = input("Enter your password: ")

    data = {"email": email, "password": password}
    response = requests.post(f"{AUTH_URL}/login", json=data)

    # Print the response for debugging
    print("Response status:", response.status_code)
    print("Response JSON:", response.json())

    if response.status_code == 200:
        jwt_token = response.json().get("token")

        if jwt_token:
            print("Login successful!")

            # Decode the JWT token to extract organization_id
            decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})  # Decode without verifying signature (for testing purposes)
            organization_id = decoded_token.get("org_id")  # Extract the organization ID from the token

            if organization_id:
                print(f"Organization ID: {organization_id} extracted from token.")
                return jwt_token
            else:
                print("Error: Organization ID not found in token.")
                return None
        else:
            print("Error: Missing 'token' in response.")
            return None
    else:
        print(f"Error: {response.json().get('message', 'Unknown error')}")
        return None

# View Projects Function
def get_projects():
    print("Fetching your projects...")

    # Use the stored organization_id and jwt_token for requests
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    url = f"{PROJECT_URL}/projects/organization/{organization_id}"

    response = requests.get(url, headers=headers)

    # Check if the response is successful
    if response.status_code == 200:
        try:
            projects = response.json().get("projects", [])

            if not projects:
                print("No projects found for this organization.")
                return

            print("\n--- Projects List ---")
            for proj in projects:
                print(f"Project Number: {proj['project_number']} | Client: {proj['client_name']}")
        except ValueError:
            print(f"Error: Received an invalid JSON response. Raw response: {response.text}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# View Queue Function
def get_queue():
    print("Fetching your queue...")

    # Use the stored jwt_token for requests
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    response = requests.get(f"{QUEUE_URL}/queues", headers=headers)

    if response.status_code == 200:
        queues = response.json()
        if not queues:
            print("No queues found.")
            return

        print("\n--- Queue List ---")
        for queue in queues:
            print(f"Queue ID: {queue['id']} | Project File: {queue['project_file']}")
    else:
        print(f"Error: {response.json()['message']}")

# Main CLI Function
def main():
    global jwt_token, organization_id  # Use global variables to track login state

    while True:
        print("Welcome to Syn-Q CLI")

        # Check if the user is already logged in
        if jwt_token and organization_id:
            print(f"Logged in! Welcome back.")
            next_choice = input("1. View Projects\n2. View Queue\n3. Logout\nEnter your choice: ").strip()
            if next_choice == "1":
                get_projects()
            elif next_choice == "2":
                get_queue()
            elif next_choice == "3":
                print("Logging out...")
                jwt_token = None
                organization_id = None
            else:
                print("Invalid choice. Returning to the main menu.")
        else:
            choice = input("1. Register\n2. Login\nEnter your choice: ").strip()

            if choice == "1":
                register()
            elif choice == "2":
                jwt_token = login()  # Now stores the token and organization_id for future use
                if jwt_token:
                    print("You are logged in!")
                    # Show next options after login
                    next_choice = input("1. View Projects\n2. View Queue\nEnter your choice: ").strip()
                    if next_choice == "1":
                        get_projects()
                    elif next_choice == "2":
                        get_queue()
                    else:
                        print("Invalid choice. Returning to the main menu.")
                else:
                    print("Login failed. Please try again.")
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
