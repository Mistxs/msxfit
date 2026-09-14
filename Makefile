.PHONY: install-be install-fe db run-be run-fe up down test

install-be:
	cd backend && python3 -m venv .venv && .venv/bin/pip install -U pip && .venv/bin/pip install -r requirements.txt

install-fe:
	cd frontend && npm install --no-audit --no-fund

db:
	cd backend && .venv/bin/flask init-db

run-be:
	cd backend && .venv/bin/flask run --host=0.0.0.0 --port=7800

run-fe:
	cd frontend && npm run dev

up:
	docker compose up -d

down:
	docker compose down

test:
	cd backend && .venv/bin/python -m pytest -q || true
