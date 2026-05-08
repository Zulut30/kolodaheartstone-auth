.PHONY: up down logs rebuild migrate lint test shell

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f bot

rebuild:
	docker compose up -d --build --force-recreate bot

migrate:
	docker compose exec bot alembic upgrade head

lint:
	ruff check app
	mypy app

test:
	pytest

shell:
	docker compose exec bot python

fresh:
	docker compose down -v
	docker compose up -d --build
