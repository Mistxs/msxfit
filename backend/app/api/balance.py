"""Дневной баланс и подсказка «что ещё можно сегодня».
Расход активности — это ОЦЕНКА, не точное число (см. roadmap)."""
from datetime import date

from flask import request, jsonify

from ..models import MealItem, Food, Dish, Profile, WeightEntry, Activity
from ..calc import zero, add, round_n
from ..cache import cache
from . import api_bp


def parse_date(s):
    return date.fromisoformat(s) if s else date.today()


def _targets(p):
    return {"kcal": p.target_kcal, "protein": p.target_protein_g,
            "fat": p.target_fat_g, "carbs": p.target_carbs_g}


def consumed_for(d):
    items = MealItem.query.filter_by(date=d).all()
    total = zero()
    for it in items:
        total = add(total, it.nutrition())
    return round_n(total)


def activity_for(d):
    acts = Activity.query.filter_by(date=d).all()
    return {
        "kcal": round(sum(a.kcal for a in acts), 1),
        "steps": sum(a.steps for a in acts),
        "distance_km": round(sum(a.distance_km for a in acts), 2),
    }


@api_bp.get("/balance")
def get_balance():
    d = parse_date(request.args.get("date"))
    cached = cache.get_json(f"balance:{d.isoformat()}")
    if cached:
        return jsonify(cached)

    p = Profile.query.get(1) or Profile(id=1)
    t = _targets(p)
    c = consumed_for(d)
    remaining = {k: max(0.0, t[k] - c[k]) for k in t}
    over = {k: max(0.0, c[k] - t[k]) for k in t}
    act = activity_for(d)
    latest = WeightEntry.query.order_by(WeightEntry.date.desc()).first()

    result = {
        "date": d.isoformat(),
        "consumed": c,
        "target": t,
        "remaining": round_n(remaining),
        "over": round_n(over),
        "activity": act,
        "weight": latest.weight_kg if latest else None,
        "weight_date": latest.date.isoformat() if latest else None,
    }
    cache.set_json(f"balance:{d.isoformat()}", result)
    return jsonify(result)


@api_bp.get("/balance/suggest")
def suggest():
    """Что ещё можно сегодня: подобрать порцию продукта/блюда так, чтобы
    уложиться в остаток ккал и добрать белок (обычно он — ограничивающий).
    Ранжирование — по тому, насколько порция восполняет остаток белка."""
    d = parse_date(request.args.get("date"))
    p = Profile.query.get(1) or Profile(id=1)
    t = _targets(p)
    c = consumed_for(d)
    rem = {k: max(0.0, t[k] - c[k]) for k in t}

    if rem["kcal"] <= 0:
        return jsonify(remaining=round_n(rem), suggestions=[], note="Дневной лимит ккал исчерпан.")

    candidates = []

    for f in Food.query.limit(500).all():
        kc = f.kcal or 0
        if kc <= 0:
            continue
        g_by_kcal = rem["kcal"] / kc * 100
        g_by_protein = (rem["protein"] / (f.protein or 0) * 100) if f.protein else None
        # Берём меньшее: чтобы не выйти за ккал и не сильно перебрать белок.
        cap = g_by_protein if g_by_protein else g_by_kcal
        g = min(g_by_kcal, cap, 600)
        if g <= 0:
            continue
        n = f.nutrition_for(g)
        if n["protein"] <= 0:
            continue
        candidates.append({
            "id": f.id, "name": f.name, "type": "food", "grams": round(g),
            "kcal": round(n["kcal"]), "protein": round(n["protein"], 1),
            "fat": round(n["fat"], 1), "carbs": round(n["carbs"], 1),
            "score": round(n["protein"], 1),
        })

    for dsh in Dish.query.all():
        p100 = dsh.per_100g()
        if p100["kcal"] <= 0:
            continue
        g_by_kcal = rem["kcal"] / p100["kcal"] * 100
        g_by_protein = (rem["protein"] / p100["protein"] * 100) if p100["protein"] else None
        cap = g_by_protein if g_by_protein else g_by_kcal
        g = min(g_by_kcal, cap, 800)
        if g <= 0:
            continue
        n = dsh.nutrition_for(g)
        candidates.append({
            "id": dsh.id, "name": dsh.name, "type": "dish", "grams": round(g),
            "kcal": round(n["kcal"]), "protein": round(n["protein"], 1),
            "fat": round(n["fat"], 1), "carbs": round(n["carbs"], 1),
            "score": round(n["protein"], 1),
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return jsonify(remaining=round_n(rem), suggestions=candidates[:10])
