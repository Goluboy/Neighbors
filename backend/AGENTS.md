# backend — rules

FastAPI, Python 3.13. Clean architecture in progress. Code is truth, README is intent, this file is
rules. Root `AGENTS.md` holds repo-wide rules; on conflict this file wins for `backend/`.

## Scope

Backend only. A frontend may appear later as a sibling directory with its own rules file and its own
CI workflow. Keep this file backend-only and never mix frontend tooling into `backend/`.

## Hard constraints

Non-negotiable; override everything below. On conflict stop and say so.

- Do not guess. No guessed intent, bug cause, value, path, or API. A fact comes from code, logs, a
  test, or a direct answer from the user. Otherwise read it, run it, or ask.
- Never edit generated output by hand. Change the source and regenerate.
- Comments earn their place or do not exist — in code and in configs (YAML, TOML, compose,
  workflows, `.env.example`). No narration of what sits next to it, no restating a function name,
  field list, or default value. A comment stays only for a non-obvious why: a decision, an
  invariant, a library or data workaround, a spec reference. Check first whether a better name
  removes the need. Do not delete or shorten an existing useful comment you were not asked to
  change.
- Every behavior change ships with a test that fails without it. Generated code, configs,
  migrations, and docs are the only exceptions.
- Never weaken, delete, or bypass a test to reach green. Change a test only when the requirement
  changes.
- No secrets in tracked files, logs, commits, or PRs. `backend/.env` is local; `.env.example` holds
  placeholders only.

## Commands

Run from `backend/`.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
pytest tests -v
alembic revision --autogenerate -m "schema"
alembic upgrade head
docker compose up -d db redis seaweedfs
```

Make targets: `run` · `test` · `lint` · `format` · `typecheck` · `layers` · `hooks` · `migrate` ·
`upgrade` · `up`.

## Layers

Dependency rule: `api` → `services` → `domain`. `persistence` and `infrastructure` implement ports.

- `app/domain` — rules, enums, stop-words, state machine, ports. Imports: stdlib plus
  `app.core.exceptions`.
- `app/domain/ports` — ABC only. Need an external dependency? Define the port first.
- `app/services` — use cases. Only `app.core` and `app.domain`. No SQLAlchemy, FastAPI, `app.models`,
  `app.persistence`.
- `app/persistence` — ORM models, repositories, UnitOfWork. The only layer with ORM.
- `app/infrastructure` — Redis, S3 (SeaweedFS), SMS. Import heavy SDKs lazily.
- `app/composition/container.py` — port assembly only. `lru_cache` means singleton.
- `app/api` — HTTP, Pydantic schemas, dependencies. `HTTPException` only here.

Layer check, from `backend/` — it is also a pre-commit hook and a CI step:

```bash
make layers
```

Empty output means clean.

## Two generations

Clean layers: `domain`, `services`, `persistence`, `infrastructure`, `composition`.
Scaffold: `app/models/models.py`, `app/schemas/schemas.py`, `app/api/v1/*`, `app/utils/s3.py`.
New code goes to the clean layers; do not extend the scaffold.

`app/models` and `app/persistence/models` declare the same tables on the same `Base`. Never import
both sets in one process: SQLAlchemy fails on duplicate table definitions. Alembic uses
`app.models`.

## Invariants

- Deposit is a hold, not a charge. No funds means `InsufficientFundsError` and no booking.
- Booking transitions go through `assert_transition` only.
- Item status comes from `ITEM_STATUS_BY_BOOKING` and changes with the booking.
- `disputed` is closed by a moderator only.
- Never expose phone or `address_text`. Feed returns `distance_m`.
- Enums live in `app.domain.enums` only. No duplicates.
- A service knows nothing about HTTP. Errors are `DomainError` subclasses from
  `app.core.exceptions`.
- Stop-words come from `app.domain.prohibited`.
- Stub SMS code is `1234`.

## Tests

- SQLite in-memory. Do not start PostGIS, Redis, or S3 in tests.
- `client` overrides `get_db` via `dependency_overrides`.
- Need Redis or WebSockets? Use the in-memory adapter from `app/infrastructure`.
- A test without `client`/`db_session` is not an API test.

## Required on every change

- Touched a route — update `../docs/API.md`.
- Touched a domain rule — update `app/domain` and add a transition test.
- Changing `app/core/security.py` — do not change the token format silently.
- Delete a `TODO` together with the code it describes, not before it.
- Run `make format` before committing; otherwise the hook rewrites the file for you.

## Done means

Do not call work complete, fixed, or passing until all of this holds.

1. `make test` green (`pytest tests -v`; needs `.venv` with `requirements-dev.txt`).
2. `make typecheck` green — mypy covers `app/core`, `app/domain`, `app/services` only.
3. `make layers` prints nothing.
4. `pre-commit run --all-files` green.
5. `python3 -c "from app.main import app; print(len(app.openapi()['paths']))"` reports 48 paths
   (`len(app.routes)` is unreliable: FastAPI stores included routers lazily). Added or removed a
   route — update this number in the same commit.

CI (`.github/workflows/ci.yml`, workflow "Backend CI") runs the same checks plus
`docker compose config`.

## Common agent mistakes

- `BookingService(db)` — the constructor is keyword-only: `uow`, `bookings`, `items`, `wallets`,
  `notifications`, `event_bus`. Wire it through `app/api/deps.py` and the container.
- `create_booking(user, ...)` — the service expects `renter_id: int`; pass `user.id`.
- `repo.add(dict(...))` versus `repo.add(entity)`: `BaseSqlRepo.add` puts an object into the
  session, a dict fails. Pick one contract and apply it to every repository.
- `DomainError` without error handlers surfaces as 500, not 4xx.
- A missing `@router.websocket` decorator means the route does not exist at all, and startup stays
  green.
- Enums redeclared outside `app.domain.enums`.
- A test weakened to green instead of the code fixed.
- Hand-edited formatting that `make format` would revert.

## Known gaps

`../docs/KNOWN_GAPS.md` is a dated list of known defects. Read it before touching the area it
names. Fixed an item — delete its line in the same commit.
