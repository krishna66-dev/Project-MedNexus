# MedNexus

A bilingual (English/Hindi), rule-based **triage severity identification system** built for
**personal health monitoring** and for **ASHA/ANM community health workers** across rural
and urban India. Styled in the visual language of Indian government digital health
portals (Ayushman Bharat / Digital India).

> **This is a decision-support tool. It does not diagnose disease and does not replace a
> doctor. In an emergency, go to the nearest hospital or call 108 (national ambulance).**

---

## Stack

| Layer     | Technology |
|-----------|------------|
| Frontend  | Svelte 4 + TypeScript + SCSS (Vite) |
| Backend   | Python 3.11+ + Flask (REST API) |
| Database  | PostgreSQL |
| Auth      | JWT (Flask-JWT-Extended) + bcrypt password hashing |
| i18n      | Custom Svelte store, English ⇄ Hindi toggle, persisted to `localStorage` |

---

## Project structure

```
mednexus/
├── backend/
│   ├── app.py                # Flask app factory + blueprint registration
│   ├── run.py                # Dev entrypoint
│   ├── config.py             # Env-driven configuration
│   ├── extensions.py         # db, bcrypt, jwt, migrate singletons
│   ├── models.py             # User, Patient, VitalsRecord (SQLAlchemy)
│   ├── schema.sql            # Raw PostgreSQL schema (alt. to Flask-Migrate)
│   ├── requirements.txt
│   ├── .env.example
│   ├── routes/
│   │   ├── auth.py           # /api/auth/register, /login, /me
│   │   ├── patients.py       # /api/patients (CRUD, scoped to logged-in user)
│   │   └── triage.py         # /api/triage, /api/patients/<id>/history, /api/records/<id>
│   └── utils/
│       └── triage_engine.py  # The severity-scoring logic (see below)
└── frontend/
    ├── index.html
    ├── vite.config.ts
    ├── svelte.config.js
    ├── tsconfig.json
    ├── package.json
    └── src/
        ├── main.ts / App.svelte
        ├── lib/
        │   ├── api.ts            # fetch wrapper w/ JWT bearer auth
        │   ├── stores.ts         # auth/session/patient stores
        │   ├── types.ts          # shared TS types
        │   ├── i18n/             # en.ts, hi.ts, index.ts (language store)
        │   └── components/       # Navbar, Footer, LanguageToggle, SeverityBadge, SymptomChecklist
        ├── routes/                # Home, Login, Register, Dashboard, Triage, Result, History
        └── styles/                # _variables.scss, _mixins.scss, global.scss (Gov-of-India theme)
```

---

## How the triage engine works (`backend/utils/triage_engine.py`)

A transparent, rule-based **Early Warning Score**, in the spirit of clinical scoring
frameworks such as NEWS2/MEWS, adapted for community-health-worker use:

- Each vital (BP, heart rate, respiratory rate, temperature, SpO₂, blood sugar,
  consciousness/AVPU) is scored **0–3** based on deviation from a normal adult range.
- Points sum into a total score, mapped to a **4-band triage colour**:
  - 🟢 **Green (0–2)** — Stable / routine monitoring
  - 🟡 **Yellow (3–5)** — Monitor closely / consider PHC visit
  - 🟠 **Orange (6–8)** — Needs prompt medical attention (CHC/hospital)
  - 🔴 **Red (9+)** — Emergency — seek immediate care / call 108
- **Red-flag symptoms** (e.g. chest pain, severe breathlessness, unconsciousness,
  seizure, stroke signs, severe bleeding) **force an escalation** to at least Orange/Red
  regardless of the numeric score — a safety net so no single dangerous sign gets
  diluted by otherwise-normal vitals.
- Every result carries an explicit recommendation and disclaimer in the user's
  chosen language.

This logic lives entirely server-side in one auditable file, so a clinician or health
authority can review/tune the thresholds independent of the UI.

---

## Setup

### 1. Database (PostgreSQL)

```bash
createdb mednexus_db
createuser mednexus_user -P     # set a password
psql -d mednexus_db -f backend/schema.sql
```

(Alternatively, skip `schema.sql` and use Flask-Migrate — see below.)

### 2. Backend (Flask)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY

# If using Flask-Migrate instead of schema.sql:
# flask --app app db init && flask --app app db migrate -m "init" && flask --app app db upgrade

python run.py                   # runs on http://localhost:5000
```

### 3. Frontend (Svelte + Vite)

```bash
cd frontend
npm install
npm run dev                     # runs on http://localhost:5173, proxies /api to :5000
```

Open `http://localhost:5173`. The language toggle (top-right, **EN / हि**) switches the
entire UI between English and Hindi instantly and remembers the choice.

### 4. Production build

```bash
cd frontend && npm run build    # outputs static assets to frontend/dist
```
Serve `frontend/dist` via any static host / Nginx, and run the Flask API behind
Gunicorn (`gunicorn -w 4 -b 0.0.0.0:5000 app:app`) with `FRONTEND_ORIGIN` set to your
deployed frontend URL for CORS.

---

## User roles

- **Individual (`self`)** — personal monitoring; a patient profile is auto-created
  mirroring the user's own details.
- **ASHA worker (`asha`)** / **ANM worker (`anm`)** — can register and track many
  patients in their village/ward, run assessments, and view each patient's history.

## API summary

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account (name, dob, age auto-computed, email, password, role) |
| POST | `/api/auth/login` | Login, returns JWT |
| GET  | `/api/auth/me` | Current user profile |
| GET/POST | `/api/patients` | List / register patients (scoped to logged-in user) |
| POST | `/api/triage` | Submit vitals + symptoms → computes & stores severity |
| GET  | `/api/patients/<id>/history` | Past assessments for a patient |
| GET  | `/api/records/<id>` | Single assessment result |

## Notes & next steps for a production rollout

- Add rate limiting and audit logging on auth endpoints.
- Consider Aadhaar-based e-KYC / ABHA ID integration if aligning with the actual
  Ayushman Bharat Digital Mission stack (not implemented here — out of scope for a demo).
- Add server-side input validation via `marshmallow` schemas (dependency already included).
- The severity thresholds in `triage_engine.py` should be reviewed and signed off by a
  qualified clinician before any real-world deployment.
