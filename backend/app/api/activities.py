"""Трекер активности (этап 2). Пока — ручной ввод.
Шаги и расход — оценки; 10 000 шагов НЕ являются обязательной целью (см. roadmap)."""
from datetime import date

from flask import request, jsonify

from ..extensions import db
from ..models import Activity
from ..cache import cache
from . import api_bp


def parse_date(s):
    return date.fromisoformat(s) if s else date.today()


@api_bp.get("/activities")
def list_activities():
    q = Activity.query
    if request.args.get("date"):
        q = q.filter_by(date=parse_date(request.args["date"]))
    return jsonify(activities=[a.to_dict() for a in q.order_by(Activity.date.desc()).all()])


@api_bp.post("/activities")
def add_activity():
    data = request.get_json(force=True)
    a = Activity(
        date=parse_date(data.get("date")),
        type=data.get("type", "walk"),
        steps=int(data.get("steps", 0)),
        distance_km=float(data.get("distance_km", 0)),
        duration_min=int(data.get("duration_min", 0)),
        kcal=float(data.get("kcal", 0)),
        note=data.get("note", ""),
    )
    db.session.add(a)
    db.session.commit()
    cache.invalidate_day(a.date)
    return jsonify(a.to_dict()), 201


@api_bp.delete("/activities/<int:aid>")
def del_activity(aid):
    a = Activity.query.get_or_404(aid)
    d = a.date
    db.session.delete(a)
    db.session.commit()
    cache.invalidate_day(d)
    return jsonify(ok=True)
