run:
	uvicorn app.main:app --reload

init:
	cd app/ && alembic init migrations

makemigrations:
	alembic revision --autogenerate

migrate:
	alembic upgrade head

down:
	alembic downgrade base


celery:
	celery -A app.tasks.celery:celery worker --loglevel=INFO

flower:
	celery -A app.tasks.celery:celery flower