# Trading Research + Paper Trading Platform (Phase 1)

Production-minded starter for **historical research, backtesting, optimization, robust strategy selection, and paper signal monitoring**.

## Scope
- ✅ Historical data research and backtesting
- ✅ IS/OOS split and walk-forward starter logic
- ✅ Robustness-focused candidate ranking
- ✅ Paper-trading engine with DB state persistence
- ✅ FastAPI + Streamlit + PostgreSQL + Redis + Celery scaffolding
- ✅ Telegram notification abstraction
- ✅ AI diagnostics report scaffolding
- ✅ Emergency stop / drawdown control starters
- ❌ Live execution (intentionally out of scope in phase 1)

## Quickstart
1. Copy environment:
   ```bash
   cp .env.example .env
   ```
2. Install:
   ```bash
   make install
   ```
3. Run tests:
   ```bash
   make test
   ```
4. Start stack:
   ```bash
   docker compose up --build
   ```

## Key endpoints
- `GET /health`
- `POST /webhook/signal`
- `POST /heartbeat/{engine_name}`

## Research workflow (starter)
1. Load OHLCV (CSV provider currently).
2. Split in-sample / out-of-sample.
3. Grid optimize strategy params on IS + validate on OOS.
4. Score robustness and rank candidates.
5. Run walk-forward consistency checks.
6. Promote only robust candidates to paper monitoring.

## Important TODOs
- Add richer trade lifecycle model (partial exits, fees by venue, mark-to-market snapshots).
- Add full regime detection and per-asset adaptive strategy routing.
- Add production scheduler/beat and retry policy.
- Add authn/authz and audit trails for control-plane actions.
