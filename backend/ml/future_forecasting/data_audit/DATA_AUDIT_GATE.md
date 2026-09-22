# AgriPredict-AI — Data Audit Gate (Step 1)

Date: 2026-09-18

## Purpose

This audit is a **gate before any new future-model retraining**. It does not modify the authoritative model-ready dataset or the validated 2024 model.

## Findings

### A. Historical target coverage

- 194 district-year observations in the authoritative 1997–2024 panel.
- 7 Vidarbha districts.
- 0 missing target values.
- 0 duplicate district-year observations.

### B. Target provenance

The dataset reports:

- 84 rows from ICRISAT DLD
- 35 rows from Maharashtra Agriculture Department APY sources
- 75 rows from `Prototype corrected selection (max positive yield <=1000)`
- 3 rows flagged `review`

The 75 prototype rows were cross-checked against the raw `Maharashtra_Cotton_Historical_1061rows_Prototype.csv` bundled in the project source package. All 75 reproduce a raw prototype record exactly (floating-point tolerance).

**Important:** reproducing a prototype source is not independent authoritative verification. These 75 rows therefore remain a provenance-upgrade item; they are not silently relabeled as official data.

### C. Three review rows

The existing review flags are retained:

- Nagpur 1997
- Yavatmal 1997
- Amravati 2016

Nagpur 1997 and Yavatmal 1997 reproduce the corresponding raw prototype records. Amravati 2016 does not reproduce the raw prototype record used for the project package, so it remains unresolved and MUST NOT be silently replaced.

The Maharashtra Agriculture Department's official document index currently lists `DISTRICTWISE APY-2016-17`, so that primary source is the next source to use for resolving Amravati 2016.

## Decision

**DO NOT retrain yet.**

The audit gate is passed for structural integrity but **not passed for full target provenance**.

The next data task is to obtain the official 2016–17 APY cotton row for Amravati, then independently verify the 75 prototype-derived rows where a primary/authoritative source is available.

## Protected items

Do not modify:

- `backend/data/vidarbha_cotton_model_ready_1997_2024.csv`
- `backend/ml/artifacts/final_model.pkl`
- 2024 holdout evaluation outputs

Do not remove Yavatmal or alter the existing 2024 evaluation.
