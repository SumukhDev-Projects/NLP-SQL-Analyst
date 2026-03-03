.PHONY: up down build logs test seed install-backend run-backend install-frontend run-frontend clean

# Docker
up:
	docker-compose up --build

up-d:
	docker-compose up --build -d

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

# Local dev
install-backend:
	cd backend && pip install -r requirements.txt

seed:
	python scripts/seed_db.py

run-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

install-frontend:
	cd frontend && npm install

run-frontend:
	cd frontend && npm run dev

# Testing
test:
	cd backend && python -m pytest tests/ -v

test-watch:
	cd backend && python -m pytest tests/ -v --tb=short -f

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -name "*.pyc" -delete 2>/dev/null; true
