run:
	uvicorn app.main:app --reload --port 8000

migrate:
	alembic revision --autogenerate -m "schema"

upgrade:
	alembic upgrade head

test:
	pytest tests -v

lint:
	ruff check app tests

typecheck:
	mypy

layers:
	@! grep -rn "sqlalchemy\|fastapi\|pydantic" app/domain app/services

up:
	docker compose up -d
