#!/usr/bin/env bash
# Серверный деплой: pull → deps → build → restart. Идемпотентный, безопасно перезапускать.
# Запускать на сервере: ~/msxfit/deploy/deploy.sh
set -euo pipefail

DIR=/home/mistxs/msxfit
echo "==> git pull"
cd "$DIR"
git pull --ff-only

echo "==> backend deps"
cd "$DIR/backend"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -U pip
.venv/bin/pip install -q -r requirements.txt

echo "==> init-db (idempotent)"
.venv/bin/flask init-db

echo "==> frontend build"
cd "$DIR/frontend"
npm ci
npm run build

echo "==> restart services"
sudo systemctl restart msxfit
sudo nginx -t
sudo systemctl reload nginx

echo "==> done → https://fit.mistxs.ru"
