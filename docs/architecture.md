# MedTrack — Architecture

**Version:** 0.1 | **Date:** June 2026

---

## Overview

MedTrack follows a monolith-first architecture sized for a two-facility pilot. The design is Postgres-ready and module-separable when scale demands it.

```
┌─────────────────────────────────────────────────┐
│                React Frontend                   │
│   Overview · Quality · Availability · Diversion │
│              (Vite + JSX, port 5173)            │
└──────────────────────┬──────────────────────────┘
                       │ HTTP / JSON
┌──────────────────────▼──────────────────────────┐
│              FastAPI Application                │
│                                                 │
│  /api/auth      /api/quality                    │
│  /api/availability   /api/diversion             │
│  /api/dashboard                                 │
│                                                 │
│  ┌───────────┐  ┌────────────┐  ┌───────────┐  │
│  │  Quality  │  │Availability│  │ Diversion │  │
│  │  Module   │  │  Module    │  │  Module   │  │
│  └─────┬─────┘  └─────┬──────┘  └─────┬─────┘  │
│        └──────────────┼───────────────┘        │
│                       │ SQLAlchemy ORM          │
│              ┌────────▼────────┐               │
│              │  stock_events   │               │
│              │    (shared)     │               │
│              └─────────────────┘               │
│                                                 │
│              SQLite (pilot) / Postgres (scale)  │
└─────────────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. Unified `stock_events` spine
All three modules read and write a single table rather than separate schemas. This means:
- One data entry flow powers all three intelligence layers
- Cross-module queries (e.g. diversion + quality co-occurring) are trivial joins
- No ETL pipeline needed between modules

### 2. Heuristics first, ML second
Phase 1 uses deterministic rules (keyword scan, consumption rate, threshold bands). This gives:
- Explainable outputs (auditors can verify the logic)
- No training data dependency at launch
- A clear baseline to measure ML improvement against

Phase 2 swaps in Isolation Forest (quality, diversion) and Prophet (availability) once labelled data accumulates.

### 3. SQLite for pilot, Postgres-ready
`DATABASE_URL` in `.env` controls the backend. The ORM layer (SQLAlchemy) abstracts the difference. Switch to Postgres by changing one env var and running `alembic upgrade head`.

### 4. Facility-scoped auth
Users are bound to a `facility_id`. District/admin users have `facility_id=None` and see all facilities. JWT tokens carry user ID; facility scope is enforced in query filters.

---

## Directory Structure

```
medtrack/
├── app/
│   ├── core/            # config, security, logging
│   ├── models/          # SQLAlchemy models + Pydantic schemas
│   ├── modules/
│   │   ├── quality/     # verification.py, anomaly_model.py
│   │   ├── availability/ # forecasting.py, forecast_model.py
│   │   └── diversion/   # reconciliation.py
│   ├── api/             # FastAPI routers (auth, quality, availability, diversion, dashboard)
│   ├── database.py
│   └── main.py
├── alembic/             # DB migrations
├── scripts/             # seed.py, future: import_dhis2.py
├── docs/                # PRD, architecture, business-case
└── tests/
```

---

## Data Flow

```
Facility staff logs event
        │
        ▼
POST /api/quality/events
        │
        ├──► StockEvent written to DB
        │
        ├──► Quality check runs automatically (verification.py)
        │         └──► quality_flag updated on event
        │
        ├──► Availability module re-reads updated stock_on_hand
        │         └──► days_remaining recalculated on next /risks call
        │
        └──► Diversion module reconciles on next /alerts call
                  └──► variance = received - (dispensed + returned + expired)
```

---

## Upgrade Path

| Phase | Change |
|-------|--------|
| Postgres | Change DATABASE_URL, run `alembic upgrade head` |
| ML quality | Train anomaly_model.py on labelled events, enable in verification.py |
| ML forecasting | Accumulate 90 days, train forecast_model.py per facility+medicine |
| DHIS2 import | `scripts/import_dhis2.py` (planned) reads DHIS2 API → stock_events |
| Offline sync | SQLite on device, sync on reconnect (planned Phase 3) |
| Barcode scan | Extend StockEvent with gtin field, query WHO GTIN registry |
