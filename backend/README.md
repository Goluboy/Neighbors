# Backend — «Neighbors»

Бэкенд сервиса обмена вещами между соседями (ЖК или кампус): витрина предметов,
бронирование с залогом, внутренний чат, взаимные оценки и модерация споров.
REST API на FastAPI, Python 3.13. Фронтенд живёт отдельно, в этом репозитории его нет.

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

Все команды ниже выполняются из корня проекта.

Инфраструктура (PostgreSQL + PostGIS, Redis, SeaweedFS) поднимается из
[`backend/docker-compose.yml`](docker-compose.yml):

```bash
docker compose -f backend/docker-compose.yml up -d db redis seaweedfs
```

Весь стек целиком, включая `api`:

```bash
docker compose -f backend/docker-compose.yml up -d
```

Python-окружение и зависимости:

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
```

`backend/.env` читается относительно рабочей директории, поэтому приложение,
тесты и миграции запускаются из `backend/`:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
pytest tests -v
```

SeaweedFS поднимается с S3 API на `http://localhost:8333`; креды и бакет описаны
в [`.env.example`](.env.example) и [`seaweedfs/s3.json`](seaweedfs/s3.json)
(бакет `neighbors-items` создаётся бэкендом при первом обращении к хранилищу).
Если `api` тоже запускается в Docker, в его `.env` нужен
`S3_ENDPOINT=http://seaweedfs:8333` — внутри контейнера `localhost` указывает на него самого.

Swagger UI будет доступен на `http://localhost:8000/docs`, OpenAPI — на
`http://localhost:8000/openapi.json`.

Для миграций (из `backend/`):

```bash
alembic revision --autogenerate -m "schema"
alembic upgrade head
```

`Makefile` содержит те же команды, плюс `make lint`, `make format`,
`make typecheck`, `make layers` и `make hooks` (ставит pre-commit-хуки).
Их же запускает CI (`.github/workflows/ci.yml`) — вместе с `make test` и
`docker compose -f backend/docker-compose.yml config`.
