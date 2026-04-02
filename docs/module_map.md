# Module map

- `app/core`: domain constants/enums/exceptions/interfaces/models
- `app/config`: env and YAML config loading
- `app/data`: market data providers/validators/resampling
- `app/strategies`: strategy base + registry + starter families
- `app/research`: backtest, optimizer, robustness, ranking, WFO
- `app/portfolio`: portfolio exposure and correlation checks
- `app/paper_engine`: paper brokerage lifecycle and reconciliation
- `app/risk`: drawdown policy and emergency controls
- `app/notifications`: message formatting + Telegram transport
- `app/ai_reports`: report prompt + generator abstraction
- `app/api`: FastAPI service endpoints
- `app/dashboard`: Streamlit UI pages
- `app/storage`: ORM models and repositories
- `app/workers`: Celery app and jobs
- `app/services`: heartbeat/health/reconciliation orchestration
