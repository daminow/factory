.PHONY: build up down logs bot shell worker fmt lint

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

bot:
	docker compose exec -it bot bash || true

worker:
	docker compose exec -it worker bash || true

fmt:
	@echo "Python formatting is not enforced; add black/ruff if needed"

lint:
	@echo "Run linters in CI or dev environment"

