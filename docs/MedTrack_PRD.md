# MedTrack — Product Requirements Document
*Supersedes the PharmaVigil draft. Same core thesis, expanded to three problems and a multi-country trajectory.*

## 1. Vision
One platform, three modules, one dashboard, answering three questions African public health supply chains currently answer separately or not at all: is this medicine **here** (availability), is it **real** (quality), and is it **going where it's supposed to go** (integrity/diversion). MedTrack starts in Uganda, extends to Kenya, and is architected from day one to generalize across African public health supply chains rather than being rebuilt per country.

## 2. Problem Statement — Three Documented Gaps

**Availability.** A cross-sectional study of 128 public and private-not-for-profit facilities across 48 districts in Uganda found 84% had reported a stockout of essential medicines or health supplies in the prior six months. A comparative Ghana/Kenya/Uganda survey found amoxicillin stockouts at over 14% of Ugandan facilities and 21% of Kenyan facilities. In Kenya, a 2019 service delivery survey found only 3% of facilities had all tracer essential medicines in stock on the day of the visit.

**Quality.** WHO estimates roughly 1 in 10 medicines circulating in low- and middle-income countries are substandard or falsified, costing those countries an estimated $30.5 billion a year — and WHO-commissioned modeling attributes excess child deaths in the African region directly to rising substandard-medicine prevalence.

**Integrity / diversion.** This is the gap most tooling ignores entirely. Donated and subsidized medicines are routinely diverted out of the public system: a Malawi field study found roughly 30–35% of government-purchased drugs and supplies went missing between central stores and clinics; in Togo, government audit found a third of Global Fund-donated antimalarials (worth over $1 million) had been stolen; a multi-city study found diverted subsidized malaria medicines on sale in 11 of 14 African cities surveyed. Diversion isn't just a quality or availability problem — it's the mechanism that often causes both.

These three are usually tracked by different teams with different tools, if tracked at all. MedTrack treats them as one reconciliation problem against one shared data backbone.

## 3. Product Scope — Three Modules, One Dashboard

**Module 1: Quality Triage** *(already built — existing verification module)*
Flags suspect batches/products via the verification method currently implemented. Unchanged in this redo — confirm current detection mechanism so it can be wired into the shared facility/commodity reference data.

**Module 2: Supply Visibility & Forecasting** *(new)*
Tracks stock movement per facility/commodity via `stock_events` (see §6) and flags stockout risk before it happens, using a rolling-consumption-vs-reorder-point stub at MVP.

**Module 3: Diversion & Leakage Detection** *(new)*
Reconciles what was received against what was dispensed/reported-used at a facility, and flags discrepancies beyond a configurable threshold as potential diversion or leakage — the same `stock_events` data, read a different way, plus a reported-usage feed (patient counts, dispense logs, or existing LMIS exports) to compare against.

**Unified Dashboard**
One view per facility, district, or program: stock position, stockout risk window, open quality flags, and reconciliation discrepancies — the artifact a donor partner can actually drop into PEPFAR/Global Fund reporting.

## 4. Target Users & Use Cases by Track

**Track 1 — Institutional (NDA / MoH Uganda, with Kenya's MoH/PPB as a natural follow-on)**
Regulatory-grade oversight across all three problems at national scale. Slow, background process.

**Track 2 — Donor-funded implementing partners (faster, funds the build)**
Uganda: IDI (Makerere), TASO, Malaria Consortium Uganda, Baylor-Uganda — already accountable to PEPFAR/Global Fund for both availability and quality reporting, and increasingly for safeguarding against the diversion that donors investigate directly (see Global Fund's own audit history). Kenya: comparable PEPFAR/Global Fund-funded implementers (e.g., Amref Health Africa, Kenya Red Cross) are realistic follow-on targets once a Uganda pilot is running — not a current outreach target, a planned second wave.

## 5. MVP Scope
- Module 1: as currently built, no changes.
- Module 2: `stock_events` ingestion (manual/CSV first) + stockout-risk stub.
- Module 3: reconciliation logic against `stock_events` + a reported-usage feed, threshold-based flagging only (no investigative workflow yet — that's v2).
- Dashboard: single facility/program view across all three modules.
- Out of scope for MVP: multi-tenant admin, automated investigation workflows, mobile app, ML-based forecasting.

## 6. Data Model
Shared backbone, `stock_events` (stack-agnostic spec, to be matched to existing repo conventions):

| Field | Notes |
|---|---|
| `id` | primary key |
| `facility_id` | FK, scoped to a `country` field at the facility level — this is what makes Kenya a data-onboarding exercise later, not a re-architecture |
| `commodity_id` | FK to existing commodity/product table |
| `event_type` | enum: receipt, dispense, adjustment, stockout_reported, reported_usage |
| `quantity` | signed integer/decimal |
| `event_time` | timestamp |
| `source` | manual, CSV import, API, LMIS feed — provenance matters more for Module 3 than Module 2 |

Module 3 needs one additional input: a `reported_usage` feed (patient counts or dispense logs) to compare against `stock_events` outflow — without it, diversion detection degrades to a stockout detector with extra steps.

## 7. Success Metrics
- Track 2: pilot partners signed, facilities reporting `stock_events`, at least one detected discrepancy (stockout-risk or reconciliation flag) validated against partner field knowledge.
- Track 1: meetings secured, any formal NDA/MoH response (low-frequency signal).
- Product: overlap rate between modules — e.g., what fraction of facilities flagged for stockout risk also carry an open quality or diversion flag. This is the number that proves the merged platform beats three separate tools.

## 8. GTM Summary
Unchanged structurally: Track 1 (NDA/MoH, slow, institutional) runs in the background; Track 2 (donor-funded partners) is the faster path that funds the build and generates the field evidence Track 1 will eventually want to see. Kenya is sequenced after a working Uganda pilot, not parallel to it — the case to a Kenyan partner is stronger with a live Uganda reference than with slideware alone.

## 9. Open Questions / Assumptions
- Current stack/ORM for the existing repo (still needed before real code).
- Exact mechanism behind the existing Quality Triage module.
- What `reported_usage` source is realistically available per partner at pilot stage (patient registers, LMIS export, something else) — this determines how strong Module 3 can actually be at MVP.
- Whether diversion flagging needs any legal/data-sensitivity review before pitching it explicitly — it's the most politically sensitive of the three modules.
