# =============================================================================
# Industriverse Database Makefile
# Week 17: Database Operations
# =============================================================================

.PHONY: help init reset migrate seed test-connection clean

# Load environment variables
include .env
export

help:
	@echo "Industriverse Database Management"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  init            Initialize database (create + schema + migrations)"
	@echo "  reset           Drop and recreate database"
	@echo "  migrate         Run pending migrations"
	@echo "  seed            Seed test data"
	@echo "  test-connection Test database connection"
	@echo "  backup          Create database backup"
	@echo "  restore         Restore from backup"
	@echo "  clean           Remove backups and temp files"
	@echo ""

init:
	@echo "Initializing database..."
	@cd scripts && ./init_db.sh

reset:
	@echo "Resetting database..."
	@export DROP_EXISTING=true && cd scripts && ./init_db.sh

migrate:
	@echo "Running migrations..."
	@for file in migrations/*.sql; do \
		echo "Applying $$file..."; \
		psql $(DATABASE_URL) -f $$file; \
	done

seed:
	@echo "Seeding test data..."
	@psql $(DATABASE_URL) -f seeds/seed_data.sql

test-connection:
	@echo "Testing database connection..."
	@psql $(DATABASE_URL) -c "SELECT version();"
	@echo ""
	@echo "Testing Redis connection..."
	@redis-cli -h $(REDIS_HOST) -p $(REDIS_PORT) PING

backup:
	@echo "Creating backup..."
	@mkdir -p backups
	@pg_dump $(DATABASE_URL) > backups/industriverse_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created: backups/industriverse_$(shell date +%Y%m%d_%H%M%S).sql"

restore:
	@echo "Restore from backup..."
	@echo "Available backups:"
	@ls -lh backups/*.sql
	@read -p "Enter backup filename: " backup_file; \
	psql $(DATABASE_URL) < backups/$$backup_file

clean:
	@echo "Cleaning backups and temp files..."
	@rm -rf backups/*.sql
	@echo "Clean complete"

# Docker-based database (for development)
docker-up:
	@echo "Starting PostgreSQL and Redis via Docker..."
	@docker-compose up -d postgres redis
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 5
	@make init

docker-down:
	@echo "Stopping Docker containers..."
	@docker-compose down

docker-logs:
	@docker-compose logs -f postgres redis
