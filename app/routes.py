from flask import Blueprint, jsonify, request
from .models import User, Project
from . import db  # Assuming db is imported from app's __init__.py

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return jsonify({"message": "Welcome to Syn-Q API!"})


@main_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()  # Get the data from the request body

    # Extract the required fields
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    org_id = data.get("organization_id")

    if not name or not email or not password or not org_id:
        return jsonify({"message": "Missing required fields"}), 400

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
