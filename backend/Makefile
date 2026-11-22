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

format:
	ruff format app tests

typecheck:
	mypy

layers:
	@! grep -rn "sqlalchemy\|fastapi\|pydantic" app/domain app/services

hooks:
	python3 -m pre_commit install

up:
	docker compose up -d

down:
	docker compose down
