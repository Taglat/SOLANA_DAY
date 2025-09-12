# Loyalty Platform | Backend

FastAPI backend for the multi-brand loyalty platform.

Local run:

- Create venv and install deps: `pip install -r requirements.txt`
- Start dev server: `uvicorn app.main:app --reload`

Docker:

- From repo root: `docker compose up --build -d backend`