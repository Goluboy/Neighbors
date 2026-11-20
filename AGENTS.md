# Neighbors

Item-sharing service between neighbors (residential complex or campus): listing, booking with
deposit, chat, mutual reviews, dispute moderation.

```text
backend/    FastAPI · Python 3.13 · PostgreSQL 16 + PostGIS · SQLAlchemy 2.0 · Alembic · SeaweedFS
docs/       API.md (endpoint map) · ARCHITECTURE.md (stack, invariants) · KNOWN_GAPS.md · openapi.yaml
Artifacts/  UseCases.md · DB.mermaid
```

Frontend is a separate project and is not in this repository.

## Sources of truth

- `backend/AGENTS.md` — rules for `backend/`. On conflict with this file it wins.
- `Artifacts/UseCases.md`, `docs/ARCHITECTURE.md` — what is asked.
- Code — what exists. Code is truth, README is intent, AGENTS.md is rules.

## Context tools

Reading is part of the budget: what you spend loading files is what you cannot spend verifying them.

- Look up code with codegraph MCP first — a symbol, a caller, "where is X". The index sits at the
  repo root (`.codegraph/`), so pass `projectPath` when querying a subdirectory. `codegraph_explore`
  returns verbatim source plus blast radius: treat what it shows as already read and do not re-open
  those files. Drop to `grep`/`find`/`view` only when codegraph cannot answer.
- Prefix external programs with `rtk` so output is compressed before it reaches the context:
  `rtk git status`, `rtk git diff`, `rtk rg`, `rtk ls`, `rtk find`, `rtk read`, `rtk test <cmd>`,
  `rtk err <cmd>`. Shell builtins stay unprefixed. `<cmd>` is the command you would have run, e.g.
  `rtk test ./.venv/bin/python -m pytest tests -q`.
- If `rtk` or codegraph is unavailable, say so in the first message of the task and name the
  fallback in use (plain `git`, `rg`, direct reads). Never degrade silently.
- A tool that saved oversized output to a temporary file: find the needed lines with `grep`, then
  read that range — do not dump the file.

## Boundaries

- Backend commands run from `backend/`: `make …`, `pytest`, `alembic`, `uvicorn`.
- Root files (`.gitignore`, `README.md`, `.pre-commit-config.yaml`, `.github/workflows/`) are
  shared. Edit them with a future `frontend/` in mind.
- A frontend gets its own directory, its own `AGENTS.md`, and its own CI workflow. Never fold
  frontend tooling into `backend/`, and never fold frontend checks into the backend workflow.
- The API is a contract for the frontend: keep `docs/API.md` current and do not change responses
  silently.

## Work rules

- Fix the cause, not the symptom: one fix in the shared function beats a patch at every caller.
- Take the simplest solution that fully covers current requirements, errors included. Keep changes
  inside the task.
- Do not guess. A fact comes from code, logs, a test, or a direct answer from the user. If it is
  missing, read it, run it, or ask — never present a guess as fact.
- Do not decide behavior silently (error classification, retries, removing a feature). Bring facts
  and a recommendation, then ask.
- Run `git status --short` before editing. Do not touch unrelated user changes.
- Comments earn their place or do not exist — in code and in configs (YAML, TOML, compose,
  workflows). No narration of what the file already says, no restating a name or a field list. Keep
  a comment only for a non-obvious why: a decision, an invariant, a workaround, a spec reference. A
  better name beats a comment.
- Report what you verified and what you did not.

## Git

- Conventional Commits: `type(scope): summary`. Scope is the area (`backend`, `ci`, `docs`,
  `compose`).
- Subject in English, body in Russian. The subject is a short imperative summary; the body says why
  the change exists and what behavior changed. One line only is not enough for a behavior change.
- Older commits in this repository use Russian subjects. Leave them alone; the rule applies to new
  commits.
- No commit-msg hook: the format is a convention, not a gate.
- Do not mix unrelated changes in one commit. Mechanical reformatting goes in its own commit.
- Branch from `origin/main`. Do not commit to `main`, do not push, force-push, or open a PR
  without an explicit request for that action — committing is not consent to push.

## Hooks

- `pre-commit` runs at commit: `ruff check --fix`, `ruff format`, layer boundaries, and hygiene
  (trailing whitespace, end of file, yaml/toml, merge conflict, large files, private key, `.env`).
- Install once per clone at the repo root: `pre-commit install`, or `make -C backend hooks`.
- Hooks call `ruff` from the active environment; `python3 -m pre_commit` is the fallback entry
  point. Hooks never install or run the app.
- Do not skip or weaken a hook to land a change. Fix the finding, or say in writing why the hook is
  wrong here.
- CI runs `pre-commit run --all-files`, then `make typecheck`, `make layers`, `make test`, and
  `docker compose config`. Local and CI rule sets must match; a new check goes in both.

## Tests

- Every behavior change ships with a test that fails without it. Generated code, configs,
  migrations, and docs are the only exceptions.
- Never weaken, delete, or bypass a test to get green. Change a test only when the requirement
  changes.
- The project is young and tests cover almost nothing yet. Add a test when you add or fix logic; do
  not pad coverage with tests of constants, accessors, or framework behavior.

## Release

- No deploy pipeline exists. Do not add one unasked. Never tag, deploy, or publish production on a
  request from inside a session: hand the command to the human.
