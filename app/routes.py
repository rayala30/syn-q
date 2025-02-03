from flask import Blueprint, jsonify, request

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return jsonify({"message": "Welcome to Syn-Q API!"})

