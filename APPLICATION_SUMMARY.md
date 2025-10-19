# Product Listing System — Application Summary

This document summarizes the Product Listing System repository: purpose, architecture, core files, API endpoints, data shapes, tests, how to run, verification, and next steps.

## Purpose
A small web service to ingest seller files (CSV/XLSX), define marketplace templates, create mappings and transformations, validate transformed data, and store results. Useful as a take-home assignment or a small production prototype.

## Architecture
- FastAPI + Uvicorn for HTTP API and OpenAPI docs.
- SQLAlchemy ORM for persistence; Postgres for containerized runs and SQLite for tests.
- pandas/openpyxl for CSV/Excel parsing.
- Pydantic v2 for request/response schemas.
- pytest for unit and integration tests.

## Key files and structure
- `app/`
  - `main.py` — creates FastAPI `app` and startup table creation.
  - `database.py` — SQLAlchemy engine, SessionLocal, `Base` declarative base.
  - `models.py` — SQLAlchemy models: `MarketplaceTemplate`, `SellerFile`, `Mapping`.
  - `schemas.py` — Pydantic request/response schemas.
  - `routers/`
    - `marketplace.py` — marketplace template CRUD.
    - `seller_file.py` — upload and list seller files.
    - `mapping.py` — create mapping, transform data, validate, fetch transformed results.
  - `services/`
    - `file_parser.py` — parse CSV/XLSX files into columns, sample_rows, row_count.
    - `transformation.py` — transformation engine logic.
    - `validation.py` — validation against marketplace templates.

- `tests/` — pytest tests (unit + integration) and fixtures.
- `requirements.txt` — pinned dependencies.
- `Dockerfile`, `docker-compose.yml` — container configuration for app + Postgres.
- `scripts/` — helper scripts (large-file generator, debug helpers).

## API Endpoints (summary)
- `GET /` — root
- `GET /health` — health check
- `POST /api/marketplace/templates` — create a marketplace template
- `GET /api/marketplace/templates` — list templates
- `POST /api/seller-file/upload` — upload seller CSV/XLSX (multipart/form-data)
- `GET /api/seller-file/files` — list uploaded files
- `POST /api/mapping/` — create a mapping, run transform+validation
- `GET /api/mapping/{id}/transformed-data` — fetch transformed data and stats

## Data shapes
- Marketplace template stored as JSON in DB; attributes contain `name`, `type`, `required`, and optional rules like `max_length`, `min_value`.
- Seller file metadata stores columns (list), sample rows (list of dicts), and row_count.
- Mapping stores column mappings list and the transformed_data (list of row dicts) and validation results.

## How to run locally
1. Activate venv (Windows):

```bash
source venv/Scripts/activate
```

2. Install dependencies (if needed):

```bash
venv/Scripts/pip.exe install -r requirements.txt
```

3. Run tests:

```bash
venv/Scripts/python.exe -m pytest -q
```

4. Run the app locally:

```bash
venv/Scripts/python.exe -m uvicorn app.main:app --reload
```

5. Run with Docker Compose:

```bash
docker-compose up --build
```

Open `http://127.0.0.1:8000/docs` for Swagger UI.

## Tests and verification
- The project includes unit tests for file parsing and transformation, and integration tests via FastAPI TestClient.
- In the current environment, test results: `25 passed, 0 failed`.

## Known issues / warnings
- Pydantic v2 deprecation warnings (class-based `Config` and `.dict()` usage). Migrate to `ConfigDict` and `model_dump()`.
- FastAPI `on_event` startup handlers produce a deprecation warning — consider using lifespan handlers.
- For very large files, pandas may use lots of memory; consider streaming/chunked processing.

## Recommended next steps
1. Migrate Pydantic/ FastAPI deprecations.
2. Add CI (GitHub Actions) to run tests on PRs.
3. Implement streaming parsing for very large seller files to reduce memory usage.
4. Add monitoring, logs, and rate-limiting if exposing publicly.

---

Generated automatically by the repository assistant. Run `pytest` to re-validate after any change.