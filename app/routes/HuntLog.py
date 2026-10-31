from flask import Blueprint, jsonify, request

from .. import db
from ..models import HuntLog, WantedCriminal

log_bp = Blueprint("hunts", __name__)

PATCHABLE = {"success", "notes"}


def error(message, code):
    return jsonify({"error": message}), code


def is_int(value):
    # bool is a subclass of int in Python, so exclude it explicitly
    return isinstance(value, int) and not isinstance(value, bool)


def validate_success_and_notes(data):
    """Check types of the optional fields. Returns an error message or None."""
    if "success" in data and not isinstance(data["success"], bool):
        return "success must be true or false"
    if "notes" in data and not isinstance(data["notes"], str):
        return "notes must be a string"
    return None


# GET /api/hunts/?criminal_id=
@log_bp.get("/")
def list_hunts():
    query = HuntLog.query
    raw = request.args.get("criminal_id")
    if raw is not None:
        try:
            criminal_id = int(raw)
        except ValueError:
            return error("criminal_id must be an integer", 400)
        if db.session.get(WantedCriminal, criminal_id) is None:
            return error(f"Criminal {criminal_id} not found", 404)
        query = query.filter_by(criminal_id=criminal_id)

    hunts = query.order_by(HuntLog.id).all()
    return jsonify([h.to_dict() for h in hunts]), 200


# GET /api/hunts/<id>/
@log_bp.get("/<int:hunt_id>/")
def get_hunt(hunt_id):
    hunt = db.session.get(HuntLog, hunt_id)
    if hunt is None:
        return error(f"Hunt log {hunt_id} not found", 404)
    return jsonify(hunt.to_dict()), 200


# POST /api/hunts/  body: {criminal_id, success?, notes?}
@log_bp.post("/")
def create_hunt():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("Request body must be a JSON object", 400)

    criminal_id = data.get("criminal_id")
    if criminal_id is None:
        return error("criminal_id is required", 400)
    if not is_int(criminal_id):
        return error("criminal_id must be an integer", 400)
    if db.session.get(WantedCriminal, criminal_id) is None:
        return error(f"Criminal {criminal_id} does not exist", 400)

    message = validate_success_and_notes(data)
    if message:
        return error(message, 400)

    # created_at is NOT read from the body: the model default sets it on the server
    hunt = HuntLog(
        criminal_id=criminal_id,
        success=data.get("success", False),
        notes=data.get("notes", ""),
    )
    db.session.add(hunt)
    db.session.commit()
    return jsonify(hunt.to_dict()), 201


# PATCH /api/hunts/<id>/  body: {success?, notes?}
@log_bp.patch("/<int:hunt_id>/")
def update_hunt(hunt_id):
    hunt = db.session.get(HuntLog, hunt_id)
    if hunt is None:
        return error(f"Hunt log {hunt_id} not found", 404)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("Request body must be a JSON object", 400)

    extra = set(data) - PATCHABLE
    if extra:
        return error(f"Only success and notes can be updated, got: {', '.join(sorted(extra))}", 400)
    if not data:
        return error("Send success and/or notes", 400)

    message = validate_success_and_notes(data)
    if message:
        return error(message, 400)

    for field in PATCHABLE & set(data):
        setattr(hunt, field, data[field])
    db.session.commit()
    return jsonify(hunt.to_dict()), 200


# DELETE /api/hunts/<id>/
@log_bp.delete("/<int:hunt_id>/")
def delete_hunt(hunt_id):
    hunt = db.session.get(HuntLog, hunt_id)
    if hunt is None:
        return error(f"Hunt log {hunt_id} not found", 404)
    db.session.delete(hunt)
    db.session.commit()
    return "", 204