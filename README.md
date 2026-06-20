# MedTrack

A-powered pharmaceutical intelligence for medicine quality, supply availability, and diversion detection.

## The problem

Health systems lose medicines at every stage of the supply chain, and most of that loss is invisible until a clinic shelf is already empty. Each module below is grounded in documented field research rather than assumption:

- **Quality** — substandard and falsified medicines remain a persistent, measurable risk in low- and middle-income health systems, as documented by the WHO and peer-reviewed literature (BMC, PLOS).
- **Availability** — facility-level stockouts are common even when national-level procurement looks adequate on paper. The gap is visibility, not just supply.
- **Diversion** — donated and government-purchased medicines disappear before reaching patients at meaningful scale. Field studies in Malawi found 30–35% of government-purchased drugs went missing before reaching clinics; Togo lost over $1M in Global Fund-supplied antimalarials to theft.

MedTrack treats these as one connected problem instead of three separate ones, because in practice they are. A stockout, a diversion event, and a quality failure can look identical from a clinic's point of view until there's data to tell them apart.

## What it does

| Module | Function |
|---|---|
| **Quality Verification** | Verifies medicine authenticity and quality at point of dispensing |
| **Availability / Forecasting** | Predicts stockout risk from supply-chain event history |
| **Diversion Detection** | Flags abnormal loss by reconciling received vs. dispensed volumes |

All three modules read and write a shared `stock_events` data model, so one pipeline of medicine-movement data powers quality checks, supply forecasts, and diversion alerts together — rather than three disconnected tools.

## Tech stack

- **Backend**: Python 3 / FastAPI
- **Data**: SQLAlchemy ORM, SQLite for pilot deployments (Postgres-ready for scale)
- **Design principle**: country-agnostic data model from day one

## Project status

Early-stage. PRD, architecture documentation, and business case are complete. The repo scaffold is in progress — the original quality-verification logic is being merged in, and the dataset acquisition plan is being finalized in parallel.

## Project structure

```
medtrack/
├── app/
│   ├── main.py                       # FastAPI entrypoint
│   ├── database.py                   # SQLAlchemy engine/session
│   ├── models/
│   │   └── stock_event.py            # shared stock_events model
│   ├── modules/
│   │   ├── quality/verification.py   # quality verification (stub — merge in progress)
│   │   ├── availability/forecasting.py
│   │   └── diversion/reconciliation.py
│   └── api/
│       └── dashboard.py              # combined dashboard endpoint
├── tests/
│   └── test_smoke.py
├── docs/
│   ├── PRD.md
│   ├── architecture.md
│   └── business-case.md
├── requirements.txt
└── .env.example
```

## Getting started

Run one of the setup scripts to scaffold the project and install dependencies:

- `setup-termux.sh` — Android / Termux
- `setup-vscode.sh` — macOS / Linux desktop

Then, from the project root:

```bash
uvicorn app.main:app --reload
```

## License

MedTrack is proprietary, commercially licensed software — see [LICENSE](./LICENSE). For pilot, partnership, or commercial licensing inquiries, contact PharmaLens, Uganda