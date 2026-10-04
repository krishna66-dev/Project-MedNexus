# MedNexus — ASHA Care & Action Plan Update

## What changed

The assessment result now includes an ASHA-facing action plan instead of stopping at a severity recommendation.

Each result provides:
- Severity and score
- Contributing factors
- What to do now
- What to avoid
- Referral / escalation guidance
- Follow-up guidance
- English and Hindi versions

## Safety boundary

The action plan is decision support, not a diagnosis, prescription, or cure. It intentionally avoids telling an ASHA worker to prescribe medicines or replace professional clinical judgement.

## Files changed

- `backend/utils/triage_engine.py` — added `build_action_plan()` and action-plan metadata to triage output.
- `backend/models.py` — exposes bilingual action plans for both new and existing assessment records without requiring a database migration.
- `frontend/src/lib/types.ts` — added action-plan types.
- `frontend/src/routes/Result.svelte` — redesigned the result screen with ASHA Care & Action Plan sections.
- `frontend/src/lib/i18n/en.ts` — added English labels.
- `frontend/src/lib/i18n/hi.ts` — added Hindi labels.

## Run the frontend

From `frontend/`:

```bash
npm install
npm run check
npm run build
npm run dev
```

## Run the backend

Use the existing backend setup and environment variables from `.env.example`.

**Important:** Do not publish a real `.env` file or database credentials to GitHub.
