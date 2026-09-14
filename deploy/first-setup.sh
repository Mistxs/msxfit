#!/usr/bin/env bash
# Первый запуск на свежем сервере (Debian). Запускать ОДИН РАЗ, до certbot.
# После этого обновления кода — deploy.sh (он НЕ трогает конфиг nginx,
# чтобы не затереть SSL, добавленный certbot).
#
# Запуск:  bash deploy/first-setup.sh
set -euo pipefail

sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    nginx tesseract-ocr tesseract-ocr-rus python3-venv

DIR=/home/mistxs/msxfit
if [ -d "$DIR/.git" ]; then
  cd "$DIR" && git pull --ff-only
else
  git clone --depth 1 https://github.com/Mistxs/msxfit.git "$DIR"
fi
cd "$DIR"

# Чтобы nginx (www-data) мог дойти до frontend/dist.
chmod o+x /home/mistxs

# Секреты для прод-инстанса.
if [ ! -f backend/.env ]; then
  KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
  printf 'SECRET_KEY=%s\nFLASK_DEBUG=0\n' "$KEY" > backend/.env
  echo "создан backend/.env"
fi

# systemd-юнит (gunicorn).
sudo cp deploy/msxfit.service /etc/systemd/system/msxfit.service
sudo systemctl daemon-reload
sudo systemctl enable msxfit

# nginx: HTTP-шаблон. default-сайт НЕ удаляем — иначе побочный эффект
# (IP-запросы уйдут в чужой catch-all). msxfit матчится по server_name и так.
sudo cp deploy/nginx.conf /etc/nginx/sites-available/msxfit
sudo ln -sf /etc/nginx/sites-available/msxfit /etc/nginx/sites-enabled/msxfit

# deps / build / init-db / start gunicorn / reload nginx
chmod +x deploy/deploy.sh
./deploy/deploy.sh

# HTTPS (Let's Encrypt). Требует, что A-запись fit.mistxs.ru уже смотрит на этот сервер.
sudo certbot --nginx -d fit.mistxs.ru --non-interactive --agree-tos \
    -m a.filippov@yclients.tech --redirect

echo "✓ done → https://fit.mistxs.ru"
