#!/bin/bash
# Запуск бота

cd "$(dirname "$0")"

# Устанавливаем зависимости если нужно
pip3 install -r requirements.txt -q

# Запускаем бота
python3 main.py
