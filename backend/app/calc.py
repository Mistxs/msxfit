"""Базовые операции над нутриентами. Все значения — в граммах / ккал.
per_100g — словарь вида {"kcal":..,"protein":..,"fat":..,"carbs":..}."""


def zero():
    return {"kcal": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0}


def scale(per_100g, grams):
    """Масштабирует нутриенты на 100 г к фактическому весу."""
    f = (grams or 0) / 100.0
    return {k: (v or 0) * f for k, v in per_100g.items()}


def add(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0) + (v or 0)
    return out


def round_n(d, n=1):
    return {k: round(v, n) for k, v in d.items()}
