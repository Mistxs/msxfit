import os

# Корень backend/ (родитель каталога app) — чтобы БД лежала в backend/instance/,
# там же, где Flask создаёт instance_path. Четыре слэша в URI — для абсолютного пути.
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    # По умолчанию SQLite в backend/instance/msxfit.db — работает из коробки без Docker.
    # Чтобы включить PostgreSQL — задай DATABASE_URL (см. .env.example).
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "instance", "msxfit.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLite + потоки (gunicorn --threads): иначе check_same_thread ругается.
    if SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
        SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"check_same_thread": False}}

    # Redis-кэш опционален: без REDIS_URL кэш просто отключается.
    REDIS_URL = os.environ.get("REDIS_URL") or ""
    CACHE_TTL = int(os.environ.get("CACHE_TTL", "300"))

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 МБ — хватит для фото этикетки
