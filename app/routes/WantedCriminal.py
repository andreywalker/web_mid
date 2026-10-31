from flask import Blueprint, jsonify, request

from .. import db
from ..models import WantedCriminal

criminals_bp = Blueprint("criminals", __name__)

BOOL_FILTERS = ["armed", "has_crew", "escape_master"]
SORTS = {"reward": WantedCriminal.reward.asc(), "-reward": WantedCriminal.reward.desc()}


def error(message, code):
    return jsonify({"error": message}), code


def parse_bool(value):
    value = value.strip().lower()
    if value in ("true", "1"):
        return True
    if value in ("false", "0"):
        return False
    raise ValueError


@criminals_bp.get("/")
def list_criminals():
    query = WantedCriminal.query

    try:
        min_reward = request.args.get("min_reward")
        max_reward = request.args.get("max_reward")
        if min_reward is not None:
            query = query.filter(WantedCriminal.reward >= int(min_reward))
        if max_reward is not None:
            query = query.filter(WantedCriminal.reward <= int(max_reward))
    except ValueError:
        return error("min_reward and max_reward must be integers", 400)

    # Boolean attributes
    for name in BOOL_FILTERS:
        raw = request.args.get(name)
        if raw is None:
            continue
        try:
            query = query.filter(getattr(WantedCriminal, name) == parse_bool(raw))
        except ValueError:
            return error(f"{name} must be true or false", 400)

    # Sorting
    sort = request.args.get("sort")
    if sort is None:
        query = query.order_by(WantedCriminal.id)
    elif sort in SORTS:
        query = query.order_by(SORTS[sort], WantedCriminal.id)
    else:
        return error("sort must be 'reward' or '-reward'", 400)

    return jsonify([c.to_dict() for c in query.all()]), 200


# GET /api/criminals/<id>/
@criminals_bp.get("/<int:criminal_id>/")
def get_criminal(criminal_id):
    criminal = db.session.get(WantedCriminal, criminal_id)
    if criminal is None:
        return error(f"Criminal {criminal_id} not found", 404)

    result = criminal.to_dict()
    result["hunts_count"] = len(criminal.hunts)
    result["captured"] = any(h.success for h in criminal.hunts)
    result["hunts"] = [
        {"id": h.id, "success": h.success, "notes": h.notes,
         "created_at": h.created_at.isoformat()}
        for h in criminal.hunts
    ]
    return jsonify(result), 200