# Tripwire: fraud rule engine with review console

FastAPI + SQLAlchemy (SQLite) backend, React (Vite) reviewer console.

## Run
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed                      # resets and seeds demo data (52 transactions)
uvicorn app.main:app --port 8000

cd frontend && npm install && npm run dev   # http://localhost:5173 (proxies /api to :8000)
```
API docs: http://localhost:8000/docs

## Adding a rule
Create a class with `name`, `weight` and `check(tx, history)` returning a reason string (or `None`),
then add it to the list in `backend/app/rules/__init__.py`. `RuleEngine` is not touched.

## AWS alerts
When a score reaches `HIGH_THRESHOLD` (default 60) an SNS alert is published if `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, `AWS_REGION` and `SNS_TOPIC_ARN` are set (see `.env.example`). Otherwise the
mock notifier logs it locally. Failures never break the request. Thresholds, weights and rule limits
are env-configurable (`app/config.py`).
