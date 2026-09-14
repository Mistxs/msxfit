from datetime import date

from flask import request, jsonify

from ..extensions import db
from ..models import WeightEntry
from . import api_bp


def parse_date(s):
    return date.fromisoformat(s) if s else date.today()


@api_bp.get("/weight")
def list_weight():
    q = WeightEntry.query
    if request.args.get("from"):
        q = q.filter(WeightEntry.date >= parse_date(request.args["from"]))
    if request.args.get("to"):
        q = q.filter(WeightEntry.date <= parse_date(request.args["to"]))
    entries = q.order_by(WeightEntry.date).all()

    # Средний вес за неделю (посние 7 записей) и изменение относительно первой записи.
    weights = [e.weight_kg for e in entries]
    weekly_avg = round(sum(weights[-7:]) / len(weights[-7:]), 1) if weights else None
    total_change = round(weights[-1] - weights[0], 1) if len(weights) >= 2 else 0.0

    return jsonify(
        entries=[e.to_dict() for e in entries],
        weekly_avg=weekly_avg,
        total_change=total_change,
    )


@api_bp.post("/weight")
def add_weight():
    data = request.get_json(force=True)
    e = WeightEntry(
        date=parse_date(data.get("date")),
        weight_kg=float(data["weight_kg"]),
        note=data.get("note", ""),
    )
    db.session.add(e)
    db.session.commit()
    return jsonify(e.to_dict()), 201


@api_bp.delete("/weight/<int:eid>")
def del_weight(eid):
    e = WeightEntry.query.get_or_404(eid)
    db.session.delete(e)
    db.session.commit()
    return jsonify(ok=True)
