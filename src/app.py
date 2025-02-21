"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure

# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# create the jackson family object
jackson_family = FamilyStructure("Jackson")


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# generate sitemap with all your endpoints
@app.route("/")
def sitemap():
    return generate_sitemap(app)


@app.route("/members", methods=["GET"])
def handle_all_members():
    try:
        return jsonify(jackson_family.get_all_members()), 200

    except Exception as e:
        response = {"error": str(e)}
        return jsonify(response), 500


@app.route("/members/<int:member_id>", methods=["GET"])
def handle_one_member(member_id):
    try:
        member = jackson_family.get_member(member_id)

        if member is None:
            response = {"error": f"Member with ID {member_id} does not exist."}
            return jsonify(response), 400

        return jsonify(member), 200

    except Exception as e:
        response = {"error": str(e)}
        return jsonify(response), 500


@app.route("/members/<int:member_id>", methods=["DELETE"])
def delete_one_member(member_id):
    try:
        member = jackson_family.get_member(member_id)

        if member is None:
            response = {"error": f"Member with ID {member_id} does not exist."}
            return jsonify(response), 400

        jackson_family.delete_member(member_id)

        return jsonify(jackson_family.get_all_members()), 200

    except Exception as e:
        response = {"error": str(e)}
        return jsonify(response), 500


@app.route("/member", methods=["POST"])
def handle_post_member():
    try:
        body = request.get_json()
        if body is None:
            return "The request body is null", 400

        if "first_name" not in body:
            return "First name not found in request body", 400

        if "id" in body:
            member_id = int(body["id"])
            if jackson_family.get_member(member_id) is not None:
                return f"Member with ID {member_id} already exists.", 400

        if "lucky_numbers" not in body or not isinstance(body["lucky_numbers"], list):
            response = {"error": f"The 'lucky_numbers' field must be a list."}
            return jsonify(response), 400

        if not body["lucky_numbers"]:
            response = {"error": f"'lucky_numbers' list cannot be empty"}
            return jsonify(response), 400

        for num in body["lucky_numbers"]:
            if not isinstance(num, int):
                response = {"error": f"All 'lucky_numbers' must be integers."}
                return jsonify(response), 400

        if "age" not in body:
            response = {"error": f"You have to write an age"}
            return jsonify(response), 400

        jackson_family.add_member(body)

        return jsonify(jackson_family.get_all_members()), 200

    except Exception as e:
        response = {"error": str(e)}
        return jsonify(response), 500


# this only runs if `$ python src/app.py` is executed
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT, debug=True)
