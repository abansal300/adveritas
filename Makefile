.PHONY: up down logs api web dbshell minio

up:
	docker-compose up --build

down:
	docker-compose down -v

logs:
	docker-compose logs -f --tail=200

api:
	open http://localhost:8000/health || true

web:
	open http://localhost:3000 || true

dbshell:
	docker exec -it adveritas-db psql -U adveritas -d adveritas

minio:
	open http://localhost:9001 || true
