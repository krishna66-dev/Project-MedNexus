# MedNexus merged frontend + Flask backend

## Backend
Use `app11.py` as the Flask backend. It keeps PostgreSQL patient verification and the existing triage engine.

Run from the backend folder:

```bash
python app11.py
```

Backend: http://127.0.0.1:5000

## Frontend
Replace your SvelteKit route file with:

```text
src/routes/+page.svelte
```

The UI is the MedNexus design supplied by the user. It connects to the Flask backend through `VITE_API_URL` and uses the existing `/` verification and `/triage` endpoints.

Create frontend `.env` if needed:

```env
VITE_API_URL=http://127.0.0.1:5000
```

The Flask backend accepts the Vite origin through `FRONTEND_URL` (default `http://localhost:5173`).

## Important
The existing Flask triage engine remains the decision source. The Svelte UI no longer uses its old local severity function for normal triage; it submits symptoms to Flask.

Pain-related cases can enter the existing Flask pain-safety flow. The current Svelte merge detects that path and asks the user to continue through the backend safety step rather than inventing a new medical rule.
