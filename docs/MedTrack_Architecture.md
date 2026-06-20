# MedTrack — Architecture Overview

## 1. Design Principles
- One shared data backbone (`stock_events` + reference data) feeding three module engines, not three separate systems bolted together.
- Country-agnostic from day one at the data model level, even though the build and pilots are Uganda-first, Kenya-second. Adding a country should mean onboarding facility/commodity reference data, not re-architecting.
- Assume low-bandwidth, partially-digitized field conditions: manual/CSV ingestion has to be a first-class path, not a fallback bolted on later — most facility-level reporting in the region still runs through manual registers or LMIS exports rather than live APIs.

## 2. System Layers

**Ingestion layer**
- Manual entry (MVP default), CSV/Excel import, and an API path for partners with existing digital systems (DHIS2, eLMIS-type tools) once available. All three feed the same `stock_events` table.

**Core data layer**
- `stock_events` (see PRD §6) plus reference tables: `facility` (with `country`, `district`, `level_of_care`), `commodity` (with program tag — HIV/TB/malaria/other, since that's how donor budgets are organized).
- `reported_usage` feed, required specifically for Module 3, sourced from whatever usage record each partner already keeps.

**Module engines** (each reads the same core data, no module owns its own silo)
- *Quality Triage* — existing engine, output is a flag attached to a `commodity_id` + `facility_id` + time window.
- *Supply Visibility & Forecasting* — rolling consumption rate (trailing window, e.g. 30 days) from `dispense` events vs. current on-hand quantity, threshold-based "days of stock remaining" alert. No seasonality or lead-time modeling at MVP.
- *Diversion & Leakage Detection* — reconciliation: expected outflow (receipts minus on-hand) vs. `reported_usage` for the same facility/commodity/window. Discrepancy beyond a configurable threshold becomes a flag, not an accusation — this module needs the most conservative thresholds and the clearest audit trail of the three, given what a false positive implies.

**Presentation layer**
- Unified dashboard: facility or program-level view combining all three flag types.
- Export path formatted for PEPFAR/Global Fund-style periodic reporting, since that's the actual artifact Track 2 partners need to produce regardless of what dashboard they're looking at day-to-day.

## 3. Multi-Country / Multi-Tenant Considerations
- `facility.country` and program-scoped `commodity` tagging mean a Kenya rollout is a data-loading exercise against the existing schema, not a fork.
- Each donor partner (IDI, TASO, Malaria Consortium, Baylor-Uganda, and later Kenya-based partners) should see only their own facilities by default — access control scoped at the facility/program level, not just a global admin/user split. This matters more for Track 2 credibility than it might first appear: partners won't want their reconciliation discrepancies visible to a different implementing partner.

## 4. Security & Data Governance
- Facility-level commodity data isn't patient-level PII in most cases, but `reported_usage` data might brush up against patient counts — treat it as sensitive by default and keep aggregation at facility level, not individual patient level, unless a partner explicitly needs more granularity.
- Module 3 specifically needs an audit log (who flagged what, when, based on which underlying events) — both because diversion findings are sensitive and because Track 1 (NDA/MoH) will expect defensible evidence trails, not just dashboard colors.
- Data-sharing terms with each Track 2 partner should be explicit about who owns the underlying data and who can see cross-partner aggregates, if any — flag this for legal review before it becomes a pilot blocker.

## 5. Integration Points (priority order for MVP)
1. CSV/manual entry — ship first, works everywhere immediately.
2. DHIS2 — widely used by MoH in both Uganda and Kenya; even read-only pull of relevant indicators would reduce partner data-entry burden significantly.
3. Partner-specific LMIS/eLMIS exports — case-by-case, likely the main source of `reported_usage` for Module 3 at pilot stage.
4. Direct API ingestion — post-MVP, once a partner's internal systems are mapped.

## 6. Open Technical Decisions
- Stack/ORM for the existing repo — needed before any of this becomes real code rather than spec. Send over the repo (zip upload here) or just the stack, and the `stock_events` model plus forecasting and reconciliation stubs can be written against your actual conventions instead of this stack-agnostic version.
- Forecasting and reconciliation logic above are intentionally simple (rolling averages, threshold flags) — appropriate for MVP and for explaining to a non-technical partner stakeholder, but should be flagged to partners as a starting point, not a finished model.
