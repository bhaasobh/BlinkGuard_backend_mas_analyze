# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Overview

This is a Python FastAPI backend for Blinkguard spam and phishing analysis. It accepts message text, runs a Hugging Face text-classification model, combines that result with psychology-rule scoring, and can save phishing reports to MongoDB.

Keep changes small and aligned with the current structure. Do not move domain logic unless the task explicitly asks for a refactor.

## Runtime Entry Points

- `server.py` is the executable entry point. Running `python server.py` starts uvicorn.
- `app/main.py` creates the `FastAPI` app and includes routers.
- `run_server.bat` starts the same server on Windows.

## Current Architecture

- `app/routes/` registers HTTP routes.
  - `analysis_routes.py` registers protected `POST /analyze` and `POST /report`.
  - `health_routes.py` registers public `GET /`.
- `app/controllers/` contains request handler logic.
  - `analysis_controller.py` validates request content, calls analysis code, and saves phishing reports.
- `app/middleware/` contains request protection dependencies.
  - `auth.py` verifies `X-Internal-Api-Key` against `INTERNAL_API_KEY`.
- `app/models/` contains Pydantic request and response schemas.
  - `analysis.py` defines `AnalysisRequest`, `ReportRequest`, and `AnalysisResponse`.
- `app/config.py` loads `.env`, configures logging, exposes `INTERNAL_API_KEY`, and reads the server port.
- `analyze_message.py` contains the core phishing/spam scoring pipeline.
- `psychology_rules.py` contains keyword and regex-based psychological risk rules.
- `mongodb_handler.py` contains MongoDB persistence using Motor.
- `train_model.py` trains and saves a classifier using `dataset/SMSSpamCollection`.

## Request Flow

`POST /analyze`:

1. `app/routes/analysis_routes.py` applies API-key auth.
2. `app/controllers/analysis_controller.py` validates that `message` is not empty.
3. `analyze_message.analyze_message()` runs ML classification and psychology scoring.
4. If `final_decision == "phishing"`, the message is saved through `mongodb_handler.save_phishing_message()`.
5. The result is returned as `AnalysisResponse`.

`POST /report`:

1. API-key auth is applied by the route.
2. The controller validates that `message` is not empty.
3. The message and metadata are saved to MongoDB as a frontend report.

`GET /`:

Public health/info endpoint. It does not require the internal API key.

## Security Notes

- `POST /analyze` and `POST /report` must stay protected by `verify_internal_api_key`.
- Clients must send `X-Internal-Api-Key`.
- Never commit `.env` or real secret values.
- If a secret appears in chat, logs, or source, assume it is exposed and rotate it.
- Use HTTPS in deployed environments so the API key is not sent over plaintext.

## Environment Variables

Expected `.env` keys:

```env
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>/<dbname>
PORT=3000
INTERNAL_API_KEY=<long-random-secret>
```

`MONGO_URI` is consumed by `mongodb_handler.py`.
`INTERNAL_API_KEY` is consumed by `app/middleware/auth.py` through `app/config.py`.
`PORT` is consumed by `server.py` through `app/config.get_port()`.

## Commands

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the server:

```bash
python server.py
```

Compile-check the app after edits:

```bash
python -m py_compile server.py app/config.py app/main.py app/controllers/analysis_controller.py app/middleware/auth.py app/models/analysis.py app/routes/analysis_routes.py app/routes/health_routes.py analyze_message.py psychology_rules.py mongodb_handler.py
```

There is currently no dedicated automated test suite in the repository.

## API Examples

Analyze a message:

```bash
curl -X POST http://localhost:3000/analyze \
  -H "Content-Type: application/json" \
  -H "X-Internal-Api-Key: <long-random-secret>" \
  -d "{\"message\":\"URGENT: Verify your account now\"}"
```

Report a message:

```bash
curl -X POST http://localhost:3000/report \
  -H "Content-Type: application/json" \
  -H "X-Internal-Api-Key: <long-random-secret>" \
  -d "{\"message\":\"Suspicious message\",\"metadata\":{\"source\":\"frontend\"}}"
```

## Coding Conventions

- Prefer plain Python modules and the existing FastAPI patterns.
- Put route definitions in `app/routes/`.
- Put request handling/business orchestration in `app/controllers/`.
- Put Pydantic schemas in `app/models/`.
- Put request auth and request-level dependencies in `app/middleware/`.
- Keep ML scoring changes in `analyze_message.py`.
- Keep psychology keyword/regex rule changes in `psychology_rules.py`.
- Keep database persistence changes in `mongodb_handler.py`.
- Avoid adding new dependencies unless necessary.
- Avoid printing secrets or full request payloads in logs.
- Use `logger` for application logs in new server code instead of `print`.

## Data And Large Artifacts

These are ignored by Git and should usually not be edited by agents unless explicitly requested:

- `dataset/`
- `results/`
- `spam_model/`
- `spam_model.zip`
- presentation or binary documentation files such as `*.pptx` and `*.pdf`

## Known Behavior To Preserve

- The Hugging Face model repo used at runtime is `bahaasobeh/blinkguard`.
- The ML model is loaded lazily the first time analysis runs.
- `LABEL_1` means spam and contributes directly to phishing risk.
- `final_decision` values are `phishing`, `suspicious`, or `not phishing`.
- `risk_band` values are `high`, `medium`, or `low`.
- Phishing analysis results are saved only when `final_decision == "phishing"`.
- Direct reports are saved with `source: frontend_report`.
