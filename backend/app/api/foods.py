from flask import request, jsonify

from ..extensions import db
from ..models import Food
from . import api_bp


@api_bp.get("/foods")
def list_foods():
    q = request.args.get("q", "").strip().lower()
    foods = Food.query.order_by(Food.name).all()
    if q:
        # Python-side: SQLite LIKE/lower сворачивают только ASCII — для кириллицы
        # регистронезависимый поиск делаем сами, с правильным Unicode-casefolding.
        foods = [f for f in foods if q in (f.name or "").lower() or q in (f.brand or "").lower()]
    return jsonify(foods=[f.to_dict() for f in foods[:200]])


@api_bp.post("/foods")
def create_food():
    data = request.get_json(force=True)
    food = Food(
        name=data["name"], brand=data.get("brand", ""),
        kcal=float(data["kcal"]), protein=float(data["protein"]),
        fat=float(data["fat"]), carbs=float(data["carbs"]),
    )
    db.session.add(food)
    db.session.commit()
    return jsonify(food.to_dict()), 201


@api_bp.get("/foods/<int:fid>")
def get_food(fid):
    return jsonify(Food.query.get_or_404(fid).to_dict())


@api_bp.put("/foods/<int:fid>")
def update_food(fid):
    food = Food.query.get_or_404(fid)
    data = request.get_json(force=True)
    for k in ("name", "brand", "kcal", "protein", "fat", "carbs"):
        if k in data:
            setattr(food, k, data[k])
    db.session.commit()
    return jsonify(food.to_dict())


@api_bp.delete("/foods/<int:fid>")
def delete_food(fid):
    food = Food.query.get_or_404(fid)
    db.session.delete(food)
    db.session.commit()
    return jsonify(ok=True)
