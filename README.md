# Backend template

A FastAPI starter with clean layering (API → service → repository → model),
dependency injection, async SQLModel/PostgreSQL, JWT auth, and an MCP tool
surface. Ships with a single `User` domain you can copy as the pattern for new
resources.

## Stack

- **FastAPI** (+ `fastapi[standard]`) for HTTP and OpenAPI
- **fastapi-mcp** to expose endpoints tagged `mcp-tools` as MCP tools at `/mcp`
- **SQLModel** + async **SQLAlchemy** + **asyncpg** (PostgreSQL)
- **dependency-injector** for wiring config / DB / repositories / services
- **PyJWT** + PBKDF2 password hashing for auth
- **loguru** / Rich logging, **asgi-correlation-id**, optional **Sentry**
- Tooling: **uv**, **ruff**, **mypy**, **pytest**

## Layout

```
src/
  main.py            ASGI app factory (AppCreator) — exports `app`
  core/              config, DI container, database, security (JWT), events, exceptions
  api/
    routes.py        aggregates versioned routers under /api/v1
    mcps.py          placeholder router for MCP-only endpoints
    endpoints/
      health.py      GET /health, /health/detailed   (public)
      users.py       /api/v1/users CRUD + auth        (JWT-protected, except register/login)
  models/            SQLModel tables (BaseModel + User)
  schemas/           Pydantic request/response DTOs
  repository/        generic CRUD repository + UsersRepository
  services/          business logic (BaseService + UsersService)
  util/              singleton, query builder, schema helpers
tests/               pytest (DB-free unit tests for health/security/validation)
```

## Quickstart

```bash
cp .env.example .env          # then edit DB_* and JWT_SECRET_KEY
uv sync                       # install deps into .venv

# Create tables (dev convenience; use migrations for real projects)
uv run python -c "import asyncio; from src.main import db; asyncio.run(db.create_database())"

# Run the API
uv run uvicorn src.main:app --reload
# OpenAPI docs:  http://127.0.0.1:8000/docs
# MCP endpoint:  http://127.0.0.1:8000/mcp
```

`uv run uvicorn main:app` also works (root `main.py` re-exports `app`).

## Auth flow

| Method | Path                     | Access            | MCP tool     |
| ------ | ------------------------ | ----------------- | ------------ |
| POST   | `/api/v1/users/register` | public            | -            |
| POST   | `/api/v1/users/login`    | public            | -            |
| GET    | `/api/v1/users/me`       | any logged-in     | -            |
| GET    | `/api/v1/users`          | admin only        | `list_users` |
| GET    | `/api/v1/users/{id}`     | self or admin     | `get_user`   |
| PATCH  | `/api/v1/users/{id}`     | self or admin     | -            |
| DELETE | `/api/v1/users/{id}`     | self or admin     | -            |
| GET    | `/health`, `/health/detailed` | public       | -            |

Access control: a Bearer token is required for everything except register, login,
and health. Ownership is enforced (you can only read/update/delete your own
account); admins (`is_superuser`) may act on any account and list all users. The
public update schema deliberately omits `is_active` / `is_superuser` to prevent
mass-assignment privilege escalation.

`register` always creates a non-admin user. Promote the first admin out-of-band,
e.g. `UPDATE users SET is_superuser = true WHERE email = 'you@example.com';`
(or in a seed script / migration).

```bash
# register, then login to get a token
curl -s localhost:8000/api/v1/users/register \
  -H 'content-type: application/json' \
  -d '{"email":"a@b.com","password":"Password1","full_name":"A B"}'

TOKEN=$(curl -s localhost:8000/api/v1/users/login \
  -H 'content-type: application/json' \
  -d '{"email":"a@b.com","password":"Password1"}' | python -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

curl -s localhost:8000/api/v1/users/me -H "authorization: Bearer $TOKEN"
```

## Adding a new resource

Copy the `User` slice: `models/<x>.py`, `schemas/<x>_schemas.py`,
`repository/<x>_repository.py` (subclass `BaseRepository`),
`services/<x>_service.py` (subclass `BaseService`), `api/endpoints/<x>.py`,
then register the repository/service in `core/container.py`, add the module to
the container's `wiring_config`, and include the router in `api/routes.py`.

## Dev commands

```bash
uv run ruff check .
uv run ruff format .
uv run mypy src
uv run pytest
```

## Docker

```bash
docker build -t backend .
docker run --rm -p 8000:8000 --env-file .env backend
```
