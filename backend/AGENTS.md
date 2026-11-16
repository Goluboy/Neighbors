# AGENTS.md — backend

FastAPI, Python 3.12. Clean architecture in progress.
Code is truth. README is intent. This file is rules.

## Order
1. `../Artifacts/UseCases.md`, `../docs/API.md` — what is asked.
2. `grep -rn "UC-" app` — where it started.
3. Tests before edit. They fail on import now. See "Broken now".
4. One task. One layer at a time.
5. Ship with `pytest tests -v` and clean layer grep.

## Commands
```
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
pytest tests -v
alembic revision --autogenerate -m "schema"
alembic upgrade head
docker compose up -d db redis seaweedfs
```
`make` broken: spaces, not tabs, `missing separator`. Run commands direct. Edit Makefile — use tabs.

## Layers
Dependency rule: `api` → `services` → `domain`. `persistence` and `infrastructure` implement ports.

- `app/domain` — rules, enums, stop-words, state machine, ports. Imports: stdlib + `app.core.exceptions`.
- `app/domain/ports` — ABC only. Need external dependency — define port first.
- `app/services` — use cases. Only `app.core`, `app.domain`. No SQLAlchemy, FastAPI, `app.models`, `app.persistence`.
- `app/persistence` — ORM models, repositories, UnitOfWork. Only layer with ORM.
- `app/infrastructure` — Redis, S3 (SeaweedFS), SMS. Import heavy SDKs lazily.
- `app/composition/container.py` — only port assembly. `lru_cache` = singleton.
- `app/api` — HTTP, Pydantic schemas, dependencies. `HTTPException` here only.

Layer check:
```
grep -rn "sqlalchemy\|fastapi\|pydantic" app/domain app/services
```
Empty = clean.

## Two generations
Clean layers: `domain`, `services`, `persistence`, `infrastructure`, `composition`.
Scaffold: `app/models/models.py`, `app/schemas/schemas.py`, `app/api/v1/*`, `app/utils/s3.py`.
New code — clean layers. Do not extend scaffold.
`app/models` and `app/persistence/models` declare same tables on same `Base`. Never import both sets in one process: SQLAlchemy fails on duplicates. Alembic uses `app.models`.

## Invariants
- Deposit is hold, not charge. No funds — `InsufficientFundsError`, no booking.
- Booking transitions — `assert_transition` only.
- Item status — from `ITEM_STATUS_BY_BOOKING`, changes with booking.
- `disputed` closed by moderator only.
- Never expose phone or `address_text`. Feed returns `distance_m`.
- Enums — `app.domain.enums` only. No duplicates.
- Service knows no HTTP. Errors — `DomainError` subclasses from `app.core.exceptions`.
- Stop-words — `app.domain.prohibited`.
- Stub SMS code — `1234`.

## Broken now
Read from code, not guesswork.
1. `app/api/v1/auth.py` imports `SmsCodeService`; `app/services/auth_service.py` has `AuthService`. `app.main` does not import. Tests fail. Fix API/service mismatch first.
2. `app/api/v1/bookings.py` calls `BookingService(db)`. Constructor is keyword-only: `uow`, `bookings`, `items`, `wallets`, `notifications`, `event_bus`. Wire through `app/api/deps.py` and container.
3. `create_booking(user, ...)` passes `User`; service expects `renter_id: int`. Pass `user.id`.
4. Services call `repo.add(dict(...))`; `BaseSqlRepo.add(entity)` puts object into session. Dict fails. Pick one contract, apply to every repository.
5. No `app/api/error_handlers.py`, though `app/core/exceptions.py` references it. `DomainError` becomes 500 instead of 4xx.
6. WS chat: `chat_websocket` lacks `@router.websocket`. Route absent.
7. `Makefile` — spaces. `make` does not parse.
8. `backend/docker-compose.yml`: `build: ./backend` resolves from file directory → `backend/backend`. No such directory. `api` service will not build.
9. `app/services/auth_service.py`: no `uow`, no commit (TODO). `User` and `Wallet` never persist.
10. Tests: only `/health` and route-group presence. No logic covered.

## Tests
- SQLite in-memory. Do not start PostGIS, Redis, S3 in tests.
- `client` overrides `get_db` via `dependency_overrides`.
- Need Redis or WS — use in-memory adapter from `app/infrastructure`.
- Test without `client`/`db_session` is not an API test.

## Required
- Touched a route — update `../docs/API.md`.
- Touched a rule — update `app/domain` and add transition test.
- Changing `core/security.py` — do not silently change token format.
- Secrets — `.env` only. Never in `.env.example`, never in code.
- Remove `TODO` with the code, not before.

## Done when
1. `pytest tests -v` green.
2. `python -c "from app.main import app; print(len(app.routes))"` prints 58 (53 API + `/health` + 4 service routes).
3. `grep -rn "sqlalchemy\|fastapi\|pydantic" app/domain app/services` empty.
4. No layer imports a layer above itself.
