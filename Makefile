# PhysioClinic — convenience shortcuts
.PHONY: up down build logs shell test seed migrate

up:
	docker compose up --build

upd:
	docker compose up --build -d

down:
	docker compose down

down-v:
	docker compose down -v

build:
	docker compose build

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-worker:
	docker compose logs -f celery_worker

shell:
	docker compose exec backend python manage.py shell

migrate:
	docker compose exec backend python manage.py migrate

makemigrations:
	docker compose exec backend python manage.py makemigrations

seed:
	docker compose exec backend python manage.py seed_data

test:
	docker compose exec backend python manage.py test --verbosity=2

test-cov:
	docker compose exec backend bash -c "pip install coverage -q && coverage run manage.py test && coverage report --omit='*/migrations/*'"

ps:
	docker compose ps
