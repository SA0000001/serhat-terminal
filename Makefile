.PHONY: install test lint run-api run-dashboard worker migrate upgrade

install:
	pip install -e .[dev]

test:
	pytest -q

lint:
	ruff check app tests

run-api:
	uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

run-dashboard:
	streamlit run app/dashboard/app.py --server.port 8501

worker:
	celery -A app.workers.celery_app worker -l info

migrate:
	alembic revision --autogenerate -m "init"

upgrade:
	alembic upgrade head
