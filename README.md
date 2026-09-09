# Task Manager

Персональный менеджер задач на Django. У каждой задачи есть срок и приоритет; выполненные и просроченные задачи визуально различаются.

## Возможности

- регистрация, вход и POST-выход;
- изолированные пользовательские списки;
- создание, редактирование и удаление с подтверждением;
- изменение статуса только POST-запросом;
- deadline, priority, completed и overdue-состояния;
- защита всех чужих объектов, admin и тесты.

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Проверки: `python manage.py check && python manage.py test`.

## Docker

Скопируйте `.env.example` в `.env`, затем `docker compose up --build`. Порт: `8003`.

Hub: https://github.com/Denbay0/practice_hub

## Screenshots

Скриншоты можно добавить в `docs/screenshots/` после запуска.
