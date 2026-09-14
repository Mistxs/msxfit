"""Распознавание этикетки: фото → OCR (Apple Vision → tesseract) → разбор КБЖУ.

Pipeline (на Маке): Apple Vision (Live Text, русский) → если пусто, tesseract →
ручной ввод. Парсер толерантный: «Белки 4,5», «132 ккал», «552 кДж», «на 100 г».
"""
import base64
import io
import re

from flask import request, jsonify

from . import api_bp


def _num(s):
    """Вытащить первое число из строки; '4,5' → 4.5, 'о'/'О' считаем за ноль."""
    if s is None:
        return None
    s = s.replace(",", ".").replace("о", "0").replace("О", "0")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def _after(keyword, text, window=25):
    """Первое число ПОСЛЕ ключевого слова."""
    for m in re.finditer(keyword, text, re.IGNORECASE):
        tail = text[m.end(): m.end() + window]
        nm = re.search(r"\d[\d.,\s]{0,6}", tail)
        if nm:
            n = _num(nm.group(0))
            if n is not None:
                return n
    return None


def _before(keyword, text, window=18):
    """Первое число ПЕРЕД ключевым словом (для «132 ккал»)."""
    for m in re.finditer(keyword, text, re.IGNORECASE):
        start = max(0, m.start() - window)
        seg = text[start: m.start()]
        nm = re.search(r"(\d[\d.,\s]{0,6})\s*$", seg)
        if nm:
            n = _num(nm.group(1))
            if n is not None:
                return n
    return None


def parse_label(text):
    """Толерантный разбор КБЖУ из распознанного текста этикетки."""
    if not text:
        return {"name": "", "kcal": None, "protein": None, "fat": None, "carbs": None, "portion_g": 100}

    protein = _after(r"белк", text) or _after(r"protein", text)
    fat = _after(r"жир", text) or _after(r"fat", text)
    carbs = _after(r"углевод", text) or _after(r"carb", text)

    kcal = (
        _before(r"ккал", text)
        or _after(r"ккал", text)
        or _after(r"энерг[а-яё]*\s*(?:ценность|значение)", text)
        or _after(r"calorie", text)
    )
    # Если ккал нет, но есть кДж — переведём (1 ккал ≈ 4,184 кДж).
    if kcal is None:
        kj = _before(r"кдж", text) or _after(r"кдж", text) or _before(r"kj", text)
        if kj is not None:
            kcal = round(kj / 4.184, 1)

    return {"name": "", "kcal": kcal, "protein": protein, "fat": fat,
            "carbs": carbs, "portion_g": 100}


@api_bp.post("/ocr/label")
def ocr_label():
    raw = None
    if "image" in request.files:
        raw = request.files["image"].read()
    else:
        data = request.get_json(silent=True) or {}
        if str(data.get("image", "")).startswith("data:"):
            raw = base64.b64decode(str(data["image"]).split(",", 1)[-1])

    if not raw:
        return jsonify(error="no image"), 400

    text = ""
    backend = ""

    # 1) Apple Vision (Live Text) — первичный путь на macOS.
    try:
        from ..ocr_apple import available, recognize
        if available():
            text = recognize(raw) or ""
            backend = "apple_vision"
    except Exception as e:
        backend = f"apple_vision_error:{e.__class__.__name__}"

    # 2) tesseract — фолбэк, если Vision недоступен/пуст.
    if not text.strip():
        try:
            import pytesseract
            from PIL import Image
            text = pytesseract.image_to_string(Image.open(io.BytesIO(raw)), lang="rus+eng")
            backend = (backend + "+tesseract") if backend else "tesseract"
        except Exception as e:
            if not backend:
                backend = f"none:{e.__class__.__name__}"

    parsed = parse_label(text)
    parsed["raw_text"] = text[:1500]
    parsed["backend"] = backend

    note = ""
    if not any(parsed.get(k) for k in ("kcal", "protein", "fat", "carbs")):
        if not text.strip():
            note = "Текст не распознан. Сделайте чёткое фото этикетки при хорошем свете."
        else:
            note = "Текст распознан, но КБЖУ не найден — проверьте «Распознанный текст» и впишите вручную."
    parsed["note"] = note
    return jsonify(parsed=parsed)
