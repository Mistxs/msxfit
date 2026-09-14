from flask import request, jsonify

from ..extensions import db
from ..models import Dish, DishIngredient
from . import api_bp


@api_bp.get("/dishes")
def list_dishes():
    dishes = Dish.query.order_by(Dish.name).all()
    return jsonify(dishes=[d.to_dict() for d in dishes])


@api_bp.post("/dishes")
def create_dish():
    data = request.get_json(force=True)
    d = Dish(
        name=data["name"],
        portion_g=float(data.get("portion_g", 100)),
        manual=bool(data.get("manual", False)),
        kcal=float(data.get("kcal", 0)), protein=float(data.get("protein", 0)),
        fat=float(data.get("fat", 0)), carbs=float(data.get("carbs", 0)),
    )
    for ing in data.get("ingredients", []):
        d.ingredients.append(DishIngredient(food_id=int(ing["food_id"]), grams=float(ing["grams"])))
    db.session.add(d)
    db.session.commit()
    return jsonify(d.to_dict()), 201


@api_bp.put("/dishes/<int:did>")
def update_dish(did):
    d = Dish.query.get_or_404(did)
    data = request.get_json(force=True)
    d.name = data.get("name", d.name)
    d.portion_g = float(data.get("portion_g", d.portion_g))
    d.manual = bool(data.get("manual", d.manual))
    for k in ("kcal", "protein", "fat", "carbs"):
        if k in data:
            setattr(d, k, float(data[k]))
    if "ingredients" in data:
        d.ingredients = []
        for ing in data["ingredients"]:
            d.ingredients.append(DishIngredient(food_id=int(ing["food_id"]), grams=float(ing["grams"])))
    db.session.commit()
    return jsonify(d.to_dict())


@api_bp.delete("/dishes/<int:did>")
def delete_dish(did):
    d = Dish.query.get_or_404(did)
    db.session.delete(d)
    db.session.commit()
    return jsonify(ok=True)
