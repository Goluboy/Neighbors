# Backend — «Neighbors»

Бэкенд сервиса обмена вещами между соседями (ЖК или кампус): витрина предметов,
бронирование с залогом, внутренний чат, взаимные оценки и модерация споров.
REST API на FastAPI, Python 3.12. Фронтенд живёт отдельно, в этом репозитории его нет.

## Стек

| Слой                  | Технология                                                   |
| --------------------- | ------------------------------------------------------------ |
| HTTP API              | FastAPI, Uvicorn                                             |
| БД                    | PostgreSQL 16 + PostGIS (локально — Docker), SQLite в тестах |
| ORM и миграции        | SQLAlchemy 2.0, Alembic                                      |
| Валидация и настройки | Pydantic 2, pydantic-settings                                |
| Аутентификация        | JWT (`python-jose`), access 15 мин + refresh 30 дней         |
| Кэш и real-time       | Redis (пока заглушки в памяти)                               |
| Файлы                 | S3-совместимое хранилище, локально SeaweedFS                 |
| Тесты                 | pytest, `TestClient`, in-memory SQLite                       |

## Быстрый старт

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Инфраструктура поднимается через Docker:

```bash
docker compose up -d db redis seaweedfs
```

SeaweedFS поднимается с S3 API на `http://localhost:8333`; креды и бакет описаны
в [`.env.example`](.env.example) и [`seaweedfs/s3.json`](seaweedfs/s3.json)
(бакет `neighbors-items` создаётся бэкендом при первом обращении к хранилищу).
Если `api` тоже запускается в Docker, в его `.env` нужен
`S3_ENDPOINT=http://seaweedfs:8333` — внутри контейнера `localhost` указывает на него самого.

Запуск приложения и тестов:

```bash
uvicorn app.main:app --reload --port 8000
pytest tests -v
```

Swagger UI будет доступен на `http://localhost:8000/docs`, OpenAPI — на
`http://localhost:8000/openapi.json`. Сейчас оба шага упираются в ImportError
из раздела «Известные проблемы».

Для миграций:

```bash
alembic revision --autogenerate -m "schema"
alembic upgrade head
```

`Makefile` содержит те же команды.
