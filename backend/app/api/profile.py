from flask import request, jsonify

from ..extensions import db
from ..models import Profile
from . import api_bp


@api_bp.get("/profile")
def get_profile():
    p = Profile.query.get(1) or Profile(id=1)
    return jsonify(p.to_dict())


@api_bp.put("/profile")
def update_profile():
    p = Profile.query.get(1) or Profile(id=1)
    data = request.get_json(force=True)
    mapping = {
        "target_kcal": "target_kcal", "target_protein_g": "target_protein_g",
        "target_fat_g": "target_fat_g", "target_carbs_g": "target_carbs_g",
        "height_cm": "height_cm", "start_weight_kg": "start_weight_kg",
        "activity_level": "activity_level",
    }
    for k, col in mapping.items():
        if k in data:
            setattr(p, col, data[k] if k == "activity_level" else float(data[k]))
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict())
