"""Тонкий слой кэша поверх Redis. Опционален: без REDIS_URL все методы — no-op,
и приложение просто считает итоги на лету. Это сознательно — на старте MVP
Redis не обязателен (см. roadmap «SQLite на старте»)."""
import json


class Cache:
    def __init__(self):
        self._r = None

    def init_app(self, app):
        url = app.config.get("REDIS_URL")
        if not url:
            return
        try:
            import redis

            self._r = redis.from_url(url, decode_responses=True)
            self._r.ping()
            app.logger.info("Redis cache enabled: %s", url)
        except Exception as e:  # нет бинарника / нет соединения
            app.logger.warning("Redis unavailable, cache disabled: %s", e)
            self._r = None

    def available(self):
        return self._r is not None

    def get_json(self, key):
        if not self._r:
            return None
        v = self._r.get(key)
        return json.loads(v) if v else None

    def set_json(self, key, val, ttl=None):
        if not self._r:
            return
        self._r.setex(key, ttl or 300, json.dumps(val, default=str))

    def delete(self, key):
        if not self._r:
            return
        self._r.delete(key)

    def invalidate_day(self, day):
        """Сбросить кэш дневника/баланса на конкретную дату — после любых изменений."""
        iso = day.isoformat() if hasattr(day, "isoformat") else str(day)
        self.delete(f"diary:{iso}")
        self.delete(f"balance:{iso}")


cache = Cache()
