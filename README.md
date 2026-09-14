# msxfit

Личный дневник питания, активности и веса. Не «MyFitnessPal + Strava + Apple Health»,
а простой дневник, которым **хочется пользоваться каждый день**. MVP отвечает на три
вопроса: **что я сегодня съел, сколько двигался, что происходит с весом**.

## Стек

- **Backend**: Flask + SQLAlchemy, REST API под `/api`
- **Frontend**: Vue 3 + Vite + vue-router, мобильный-first
- **БД**: SQLite из коробки (локальная разработка), переключается на PostgreSQL через `DATABASE_URL`
- **Кэш**: Redis опционален — без `REDIS_URL` дневные итоги считаются на лету
- Сканирование этикеток: OCR через `tesseract` (опционально, с фолбэком на ручной ввод)

## Быстрый старт

```bash
# 1. Backend
make install-be        # создаст backend/.venv и установит зависимости
make db                # создаст схему + наполнит справочник продуктов

# 2. Frontend
make install-fe

# 3. Запуск (в двух терминалах)
make run-be            # Flask на http://127.0.0.1:7800
make run-fe            # Vite на http://127.0.0.1:7801
```

Откройте http://127.0.0.1:7801 — фронт ходит в API через vite-прокси.

> Цели по КБЖУ и стартовый вес задаются в **Настройках**. По умолчанию профиль
> пустой (0) — поэтому прогресс-бары на дашборде сразу выглядят «перевыполненными»,
> пока не задашь свои цели.

## Опционально: PostgreSQL + Redis

```bash
cp .env.example .env
# раскомментируйте DATABASE_URL и REDIS_URL
make up            # поднимет postgres + redis
make db            # пересоздаст схему в новой БД
```

## Распознавание этикеток (Apple Vision)

Экран «Скан» фотографирует этикетку (камера iPhone в мобильном браузере) и шлёт фото
на `POST /api/ocr/label`. На Маке распознавание идёт через **нативный Apple Vision**
(`VNRecognizeTextRequest`, тот же движок, что Live Text) — русский распознаёт уверенно,
облако не участвует. Pipeline:

1. **Apple Vision** (Live Text, ru-RU/en-US) — первичный путь; в `requirements.txt`
   как `pyobjc-framework-Vision` (только macOS).
2. **tesseract** (`brew install tesseract tesseract-lang`, модуль `pytesseract`) — фолбэк,
   если Vision недоступен или вернул пусто.
3. Ручной ввод — всегда доступен: распознанные значения подставляются в форму, ниже
   показывается «Распознанный текст» для проверки.

Парсер КБЖУ (`parse_label` в `backend/app/api/ocr.py`) толерантный: «Белки 4,5»,
«132 ккал», «552 кДж» (переводится в ккал), «Энергетическая ценность …». Для совсем
кривых фото точнее будет vision-LLM — подставьте её вызов в `recognize()` вместо
tesseract, фронт менять не нужно.

Доступ с iPhone: откройте UI по LAN-IP Мака — в `frontend/vite.config.js`
раскомментируйте `host: '0.0.0.0'` и зайдите на `http://<mac-ip>:7801`
(backend уже слушает `0.0.0.0:7800`).

## Архитектура

```
backend/
  app/
    __init__.py     # Flask factory + CLI `flask init-db`
    config.py       # DATABASE_URL / REDIS_URL / SECRET_KEY
    models.py       # Food, Dish, DishIngredient, MealItem, WeightEntry, Activity, Profile
    calc.py         # scale/sum/round над нутриентами
    cache.py        # тонкий Redis-слой (опционален)
    seed.py         # справочник продуктов по умолчанию
    api/            # REST: foods, dishes, diary, weight, profile, balance, activities, ocr
  wsgi.py           # для gunicorn/production
frontend/
  src/
    api.js          # fetch-клиент + хелперы
    router.js
    views/          # Dashboard, Diary, Foods, Dishes, Weight, Suggest, Scan, Settings
    components/     # ProgressBar, LineChart
```

### Модели (кратко)

- **Food** — продукт, КБЖУ на 100 г.
- **Dish** — блюдо: либо из ингредиентов (`manual=False`, КБЖУ считается автоматически),
  либо ручное (`manual=True`, КБЖУ на порцию). Для логирования всё приводится к
  «на 100 г».
- **MealItem** — запись дневника (дата, тип приёма пищи, продукт/блюдо, граммы).
- **WeightEntry** — запись веса.
- **Activity** — ходьба/велосипед/прочее (этап 2). `kcal` — оценка, не точное число.
- **Profile** — синглтон (id=1) с целями по КБЖУ. На этапе авторизации станет per-user.

## API (основное)

```
GET/POST/PUT/DELETE  /api/foods
GET/POST/PUT/DELETE  /api/dishes
GET/POST/PUT/DELETE  /api/diary
GET/POST/DELETE      /api/weight
GET/PUT              /api/profile
GET                  /api/balance?date=YYYY-MM-DD
GET                  /api/balance/suggest?date=YYYY-MM-DD
GET/POST/DELETE      /api/activities
POST                 /api/ocr/label   (multipart: image)
GET                  /health
```

## Соответствие роадмапу

| Этап | Статус в v0.1 |
|------|---------------|
| 1. MVP: продукты, блюда, дневник, авто-расчёт КБЖУ | ✅ |
| 2. Трекер активности (ходьба/вело) | API + UI-заготовка (`/api/activities`) — ручной ввод; графики активностей — следующая итерация |
| 3. Дневной баланс | ✅ экран «Сегодня», расход активности — как оценка |
| 4. Графики и аналитика | базово: график веса, среднее за неделю, изменение; полный набор графиков — дальше |
| 5. Apple Watch / HealthKit | не в MVP (по плану) — архитектура API готовит почву |
| 6. Авторизация + PostgreSQL + бэкапы | PostgreSQL готов к подключению; авторизация — следующий этап |

### Доп. фичи из ТЗ
- **Скан этикетки с iPhone** — экран «Скан» (`/scan`), OCR best-effort.
- **«Что ещё можно сегодня»** — экран `/suggest`: подбор порций в рамках остатка ккал с приоритетом белка.
- **Postgres + Redis** — оба подключаются одной переменной окружения, деградируют на SQLite/in-memory.

## Что дальше (приоритеты v0.2+)

- графики калорий/белка/шагов за 7/30/90 дней;
- недельные/суточные цели по активности (без обязательных 10 000 шагов);
- авторизация + users (Profile → per-user);
- миграции (Flask-Migrate) и резервное копирование PostgreSQL;
- iOS-приложение для синхронизации HealthKit → API.

## Deploy (fit.mistxs.ru)

Продакшен: gunicorn (systemd) + nginx + SQLite на сервере `spica` (Debian 13).

**Первый запуск на свежем сервере** (один раз):
```bash
ssh mistxs@<server>
git clone https://github.com/Mistxs/msxfit.git ~/msxfit
bash ~/msxfit/deploy/first-setup.sh   # apt, venv, build, systemd, nginx, certbot
```
Требует: A-запись `fit.mistxs.ru` → публичный IP сервера.

**Обновление** после изменений в коде:
```bash
ssh mistxs@<server> 'cd ~/msxfit && ./deploy/deploy.sh'   # git pull → deps → build → restart
```
`deploy.sh` НЕ перезаписывает конфиг nginx — чтобы не затереть SSL, добавленный certbot.

Состав:
- gunicorn: `--workers 1 --threads 4 -b 127.0.0.1:7800 wsgi:app` → `deploy/msxfit.service`
- nginx: SPA (`frontend/dist`) + прокси `/api` и `/health` → `127.0.0.1:7800` → `deploy/nginx.conf`
- БД: SQLite (`backend/instance/msxfit.db`); Postgres/Redis — опционально через `.env`
- HTTPS: Let's Encrypt, авто-renew (`certbot --nginx`)
- OCR: на сервере (Linux) — через tesseract; Apple Vision — только если бэкенд запущен на macOS

## Главное правило проекта

Не пытаться сразу сделать всё. Сначала — маленькое приложение, которым реально
пользуешься каждый день. Остальное — следующий этап.
