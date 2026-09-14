from flask import Blueprint

api_bp = Blueprint("api", __name__)

# Импортируем модули, чтобы их роутеры зарегистрировались в api_bp.
from . import foods, dishes, diary, weight, profile, balance, activities, ocr  # noqa: E402,F401
