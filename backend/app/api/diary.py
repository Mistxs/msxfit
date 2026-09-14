from datetime import date

from flask import request, jsonify

from ..extensions import db
from ..models import MealItem
from ..calc import zero, add, round_n
from ..cache import cache
from . import api_bp

MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack", "other"]


def parse_date(s):
    return date.fromisoformat(s) if s else date.today()


@api_bp.get("/diary")
def get_diary():
    d = parse_date(request.args.get("date"))
    cached = cache.get_json(f"diary:{d.isoformat()}")
    if cached:
        return jsonify(cached)

    items = MealItem.query.filter_by(date=d).order_by(MealItem.created_at).all()
    groups = {mt: [] for mt in MEAL_TYPES}
    total = zero()
    for it in items:
        groups.setdefault(it.meal_type, []).append(it.to_dict())
        total = add(total, it.nutrition())

    result = {"date": d.isoformat(), "items": groups, "totals": round_n(total)}
    cache.set_json(f"diary:{d.isoformat()}", result)
    return jsonify(result)


@api_bp.post("/diary")
def add_item():
    data = request.get_json(force=True)
    d = parse_date(data.get("date"))
    st = data["source_type"]
    item = MealItem(
        date=d,
        meal_type=data.get("meal_type", "other"),
        source_type=st,
        food_id=int(data["food_id"]) if st == "food" and data.get("food_id") else None,
        dish_id=int(data["dish_id"]) if st == "dish" and data.get("dish_id") else None,
        grams=float(data["grams"]),
        label=data.get("label"),
    )
    db.session.add(item)
    db.session.commit()
    cache.invalidate_day(d)
    return jsonify(item.to_dict()), 201


@api_bp.put("/diary/<int:iid>")
def update_item(iid):
    item = MealItem.query.get_or_404(iid)
    data = request.get_json(force=True)
    old_date = item.date
    if "grams" in data:
        item.grams = float(data["grams"])
    if "meal_type" in data:
        item.meal_type = data["meal_type"]
    if "date" in data:
        item.date = parse_date(data["date"])
    db.session.commit()
    cache.invalidate_day(old_date)
    if item.date != old_date:
        cache.invalidate_day(item.date)
    return jsonify(item.to_dict())


@api_bp.delete("/diary/<int:iid>")
def delete_item(iid):
    item = MealItem.query.get_or_404(iid)
    d = item.date
    db.session.delete(item)
    db.session.commit()
    cache.invalidate_day(d)
    return jsonify(ok=True)
