from flask import Blueprint, jsonify, request
from .models import User, Project, Organization
from . import db  # Assuming db is imported from app's __init__.py

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return jsonify({"message": "Welcome to Syn-Q API!"})


@main_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # Extract required fields
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    org_id = data.get("organization_id")
    org_passcode = data.get("org_passcode")  # New field

    if not name or not email or not password or not org_id or not org_passcode:
        return jsonify({"message": "Missing required fields"}), 400

    # Validate organization and passcode
    organization = Organization.query.filter_by(id=org_id).first()
    if not organization:
        return jsonify({"message": "Invalid organization ID"}), 400

    if organization.org_passcode != org_passcode:
        return jsonify({"message": "Incorrect organization passcode"}), 403  # Forbidden

    # Create a new User instance
    new_user = User(name=name, email=email, password=password, organization_id=org_id)

    # Add to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201



@main_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400

    # Query the database for the user
    user = User.query.filter_by(email=email).first()

    if user and user.password == password:
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "organization_id": user.organization_id
            }
        }), 200

    return jsonify({"message": "Invalid credentials"}), 401


@main_bp.route("/projects", methods=["GET"])
def get_projects():
    projects = Project.query.all()

    # Format the project data as a list of dictionaries
    project_list = [
        {
            "project_number": proj.project_number,
            "client_name": proj.client_name,
            "files": [{"file_name": file.file_name, "file_type": file.file_type} for file in proj.files]
        }
        for proj in projects
    ]

    return jsonify({"projects": project_list}), 200


@main_bp.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()

    user_list = [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.is_admin,
            "organization_id": user.organization_id
        }
        for user in users
    ]

    return jsonify({"users": user_list}), 200


# @main_bp.route("/organizations", methods=["GET"])
# def get_organizations():
#     organizations = Organization.query.all()
#
#     org_list = [
#         {
#             "id": org.id,
#             "name": org.name,
#             "admin_email": org.admin_email,
#             "email_domain": org.email_domain
#         }
#         for org in organizations
#     ]
#
#     return jsonify({"organizations": org_list}), 200


@main_bp.route("/organization/<int:org_id>/users", methods=["GET"])
def get_users_in_org(org_id):
    users = User.query.filter_by(organization_id=org_id).all()

    user_list = [
        {"id": user.id, "name": user.name, "email": user.email, "is_admin": user.is_admin}
        for user in users
    ]

    return jsonify({"users": user_list}), 200
