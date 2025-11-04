# Flat-Blog v8 — Админка + живой предпросмотр

## Запуск
```bash
docker compose up --build
# http://127.0.0.1:8000
# admin: http://127.0.0.1:8000/admin/  (логин admin / change_me_strong)
```
## Контент
- Посты: `content/posts/*.md`
- Страницы: `content/pages/*.md`

## Темы
Активная тема: `FLATCMS_THEME` (по умолчанию `clean`).
Стили/скрипты: `static/themes/<тема>/`.
Шаблоны: `templates/themes/<тема>/`.
