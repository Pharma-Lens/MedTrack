# MedTrack — Business Case

## 1. The Problem, Sized
Three documented, separately-tracked failure modes in African essential-medicine supply chains:

- **Availability:** 84% of 128 surveyed Ugandan facilities reported a stockout of essential medicines or supplies in the prior six months. Kenya's 2019 service delivery survey found only 3% of facilities had all tracer medicines in stock.
- **Quality:** WHO estimates roughly 1 in 10 medicines in low- and middle-income countries are substandard or falsified, costing those countries an estimated $30.5 billion annually — and WHO-modeled excess child mortality rises directly with substandard-medicine prevalence in the African region.
- **Integrity/diversion:** A Malawi field study found 30–35% of government-purchased drugs and supplies went missing between central stores and clinics. A Togo government audit found a third of Global Fund-donated antimalarials (over $1 million worth) had been stolen. Diverted subsidized malaria medicines were found on sale in 11 of 14 African cities studied.

No single tool in wide use addresses all three together, and a recent BMC-published study specifically flagged the availability/quality pairing as under-evidenced — the gap that makes MedTrack a credible response to a named problem rather than a vendor pitch.

## 2. Why Now
- Donor accountability pressure (PEPFAR/Global Fund) on implementing partners is already pushing toward better commodity reporting — MedTrack maps onto an obligation partners already have, not a new one.
- The diversion literature above (Malawi, Togo, AMFm studies) shows this isn't a hypothetical risk — donors investigate it directly, which means a partner that can show proactive monitoring has a real institutional incentive to engage, independent of altruism.

## 3. ROI — Short Term (Track 2, donor-funded pilots)
- **Cost avoidance is the easiest sell.** A single diversion incident at one country's scale was worth over $1 million (Togo). A pilot covering even a handful of facilities that surfaces one real discrepancy plausibly pays for itself many times over relative to typical pilot software costs.
- **Reporting time savings.** Partners already produce PEPFAR/Global Fund commodity reports manually from disparate sources; a unified dashboard reduces the assembly work, which is a quantifiable, low-risk value proposition independent of whether any flags ever fire.
- **Low integration cost at pilot scale.** CSV-first ingestion (per architecture doc) means a pilot doesn't require a partner to change existing systems before getting value.
- **Funds Track 1 indirectly.** Track 2 revenue/grant funding covers build costs while the NDA/MoH institutional conversation (Track 1) plays out in the background — the dataset built during Track 2 pilots becomes part of the evidence base for the Track 1 pitch.

## 4. ROI — Long Term
- **Scale economics favor this architecture.** Because the data model is country-agnostic from the start (architecture doc §3), Kenya expansion is data onboarding, not a rebuild — each additional country/partner has materially lower marginal cost than the first.
- **The absolute numbers are large.** $30.5 billion/year in LMIC spend on substandard/falsified medicines and double-digit-percentage diversion losses mean even a small percentage improvement, sustained at national scale, represents meaningful absolute savings — and, per the WHO-modeled mortality link, real reductions in preventable child deaths.
- **Switching cost compounds.** Once a partner's PEPFAR/Global Fund reporting workflow runs through MedTrack, replacing it means rebuilding that workflow elsewhere — this is a durable, not one-time, relationship.
- **Institutional credibility flywheel.** Field evidence from Track 2 pilots (real facilities, real flags, real partner validation) is exactly what a slow-moving Track 1 institutional process (NDA/MoH) would want to see before committing — each pilot makes the next conversation, on either track, easier.

## 5. Cost Structure (rough, pilot vs. scale)
- **Pilot stage:** primarily people-time (integration, partner onboarding, threshold tuning), modest infrastructure (CSV-first means no heavy systems integration cost upfront).
- **Scale stage:** infrastructure and integration costs rise with API/DHIS2 connections and multi-partner access control, but this is the stage where Track 2 partners' existing PEPFAR/Global Fund-aligned budgets — the ones specifically earmarked for commodity availability and quality — become the funding source, not the build team's own capital.

## 6. Risks
- Diversion flagging is politically sensitive — a false positive implicates real staff at real facilities. Conservative thresholds and a clear audit trail (architecture doc §4) aren't optional, they're what makes Module 3 sellable at all.
- Data access varies a lot by partner — `reported_usage` quality for Module 3 depends entirely on what each partner already collects, which means Module 3's strength will vary by pilot site in ways Modules 1 and 2 won't.
- Track 1 (NDA/MoH) timelines are genuinely unpredictable — the business case deliberately doesn't depend on Track 1 moving quickly; Track 2 alone should justify continued investment.

## 7. Bottom Line
The case doesn't rest on one big institutional win. It rests on three independently-documented, expensive problems, a partner base that's already accountable for two of them and increasingly scrutinized on the third, and an architecture where the first pilot's marginal cost is the highest one MedTrack will ever pay.


*Sources: WHO substandard/falsified medicines fact sheet and Member State Mechanism report; PLOS One Ghana/Kenya/Uganda facility survey (2014); Journal of Pharmaceutical Policy and Practice, Uganda supply chain assessment; Kenya MoH 2019 service delivery survey (via Nyeri County study); PMC field study on AMFm medicine diversion; Foreign Policy reporting on Togo Global Fund antimalarial theft; GiACE Malawi medication theft field study.*



# MedTrack — Business Case

**Version:** 0.1 | **Date:** June 2026 | **PharmaLens, Uganda**

---

## The Opportunity

Sub-Saharan Africa's pharmaceutical supply chain loses an estimated **10–30% of medicine value** before reaching patients, through a combination of quality failures, stockouts, and diversion. For Uganda alone, the Ministry of Health manages over UGX 300 billion in annual medicine procurement — meaning even a 10% improvement in supply chain visibility is worth UGX 30B+/year.

The problem is not procurement volume. It is **visibility**. National-level stock looks adequate on paper while individual clinics run empty. The gap between what was received at district level and what reached patients is rarely measured in real time.

---

## Market Segments

### Segment 1: Government Health Systems
**Buyers:** Ministry of Health, National Medical Stores (NMS Uganda), district health offices
**Pain:** No real-time visibility into facility-level stock; diversion investigations are post-hoc and manual
**Budget pathway:** MoH IT procurement, development partner funding (USAID, Global Fund, GAVI)
**Entry:** Pilot with 2–5 facilities, demonstrate diversion detection, expand via district contract

### Segment 2: NGO & Donor-Funded Programmes
**Buyers:** PEPFAR-funded clinics, MSF, IRC, Partners in Health
**Pain:** Donor accountability requirements; need to prove medicines reached intended recipients
**Budget pathway:** Overhead / monitoring & evaluation budget (typically 5–15% of programme cost)
**Entry:** Position as M&E tool; bundle with existing data collection workflow

### Segment 3: Private Pharmacy Chains
**Buyers:** AAR Healthcare, Mediplan, independent chains (East Africa)
**Pain:** Inventory shrinkage, counterfeit exposure, expiry waste
**Budget pathway:** Direct SaaS subscription
**Entry:** Lower-touch onboarding; focus on quality verification and inventory reconciliation

---

## Revenue Model

| Tier | Target | Pricing |
|------|--------|---------|
| **Pilot** | Government / NGO facilities | Free (grant/donor funded) |
| **Facility SaaS** | Private clinics and pharmacies | $50–150/facility/month |
| **District License** | Government district health offices | $500–2,000/district/year |
| **National Platform** | Ministry-level deployment | Custom contract |
| **API Access** | Procurement systems, EHR vendors | Per-call or volume pricing |

---

## Competitive Landscape

| Tool | Focus | Gap MedTrack fills |
|------|----|---|
| DHIS2 | Aggregate reporting | No real-time event-level data; no anomaly detection |
| mSupply | Inventory management | Strong on stock control; weak on diversion and quality |
| Trackpad / GS1 | Barcode track-and-trace | Hardware-dependent; not viable for low-resource facilities |
| Excel/paper | Most common in Uganda | No analytics, no alerts, no reconciliation |

MedTrack's differentiation: **unified intelligence across quality, availability, and diversion from a single lightweight data pipeline**, deployable without hardware investment.

---

## Go-to-Market: 2026

**Q3 2026 — Pilot**
- 2 facilities in Uganda (Mbarara / Kampala)
- Free deployment, PharmaLens collects data and provides support
- Goal: 500+ events logged, 1 confirmed diversion alert, stockout prediction validated

**Q4 2026 — First Revenue**
- Present pilot results to MoH ICT / NMS Uganda
- Apply for MoICT Government Systems Prototype funding
- First paying customer: NGO or private pharmacy chain

**2027 — Scale**
- 3–5 district-level contracts
- DHIS2 integration for government alignment
- East Africa expansion: Kenya (KEMSA), Tanzania (MSD)

---

## Why Now

1. Uganda's Ministry of ICT is actively funding health-tech prototypes (MoICT Showcase 2026)
2. Post-COVID supply chain failures increased political will for visibility tools
3. Global Fund and PEPFAR both introduced stronger accountability requirements post-2023
4. Mobile penetration and low-cost Android devices make web-based tools viable at facility level without dedicated hardware

---

## Ask

**Pilot phase:** In-kind technical support + introductions to 2 pilot facilities
**Seed funding:** $15,000–$30,000 to cover 6 months of development and pilot operations

Contact: PharmaLens, Uganda