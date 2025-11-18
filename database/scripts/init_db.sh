#!/bin/bash
# =============================================================================
# Database Initialization Script
# Week 17: Database Setup
# =============================================================================

set -e

echo "==============================================="
echo "Industriverse Database Initialization"
echo "==============================================="

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found. Using defaults."
fi

# Default values
DATABASE_HOST=${DATABASE_HOST:-localhost}
DATABASE_PORT=${DATABASE_PORT:-5432}
DATABASE_NAME=${DATABASE_NAME:-industriverse}
DATABASE_USER=${DATABASE_USER:-industriverse}
DATABASE_PASSWORD=${DATABASE_PASSWORD:-changeme}

echo ""
echo "Configuration:"
echo "  Host: $DATABASE_HOST"
echo "  Port: $DATABASE_PORT"
echo "  Database: $DATABASE_NAME"
echo "  User: $DATABASE_USER"
echo ""

# Check if PostgreSQL is running
echo "Checking PostgreSQL connection..."
if ! pg_isready -h $DATABASE_HOST -p $DATABASE_PORT > /dev/null 2>&1; then
    echo "Error: Cannot connect to PostgreSQL at $DATABASE_HOST:$DATABASE_PORT"
    echo "Please ensure PostgreSQL is running."
    exit 1
fi
echo "✓ PostgreSQL is running"

# Check if database exists
echo ""
echo "Checking if database exists..."
if psql -h $DATABASE_HOST -p $DATABASE_PORT -U postgres -lqt | cut -d \| -f 1 | grep -qw $DATABASE_NAME; then
    echo "✓ Database '$DATABASE_NAME' exists"

    # Ask if user wants to drop and recreate
    if [ "$DROP_EXISTING" = "true" ]; then
        echo ""
        echo "WARNING: DROP_EXISTING=true"
        echo "Dropping existing database..."
        psql -h $DATABASE_HOST -p $DATABASE_PORT -U postgres -c "DROP DATABASE IF EXISTS $DATABASE_NAME;"
        echo "Creating new database..."
        psql -h $DATABASE_HOST -p $DATABASE_PORT -U postgres -c "CREATE DATABASE $DATABASE_NAME OWNER $DATABASE_USER;"
        echo "✓ Database recreated"
    fi
else
    echo "Database '$DATABASE_NAME' does not exist. Creating..."

    # Create database user if doesn't exist
    psql -h $DATABASE_HOST -p $DATABASE_PORT -U postgres <<-EOSQL
        CREATE USER $DATABASE_USER WITH PASSWORD '$DATABASE_PASSWORD';
        ALTER USER $DATABASE_USER WITH SUPERUSER;
EOSQL

    # Create database
    psql -h $DATABASE_HOST -p $DATABASE_PORT -U postgres -c "CREATE DATABASE $DATABASE_NAME OWNER $DATABASE_USER;"
    echo "✓ Database created"
fi

# Apply schema
echo ""
echo "Applying database schema..."
export PGPASSWORD=$DATABASE_PASSWORD
psql -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER -d $DATABASE_NAME -f ../schema/unified_schema.sql

if [ $? -eq 0 ]; then
    echo "✓ Schema applied successfully"
else
    echo "✗ Schema application failed"
    exit 1
fi

# Run migrations
echo ""
echo "Running migrations..."
for migration in ../migrations/*.sql; do
    if [ -f "$migration" ]; then
        echo "  Applying: $(basename $migration)"
        psql -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER -d $DATABASE_NAME -f "$migration"
    fi
done
echo "✓ Migrations complete"

# Seed data (optional)
if [ "$SEED_DATA" = "true" ]; then
    echo ""
    echo "Seeding test data..."
    if [ -f ../seeds/seed_data.sql ]; then
        psql -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER -d $DATABASE_NAME -f ../seeds/seed_data.sql
        echo "✓ Test data seeded"
    else
        echo "⚠ No seed data file found"
    fi
fi

# Verify installation
echo ""
echo "Verifying installation..."
SCHEMA_COUNT=$(psql -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER -d $DATABASE_NAME -t -c "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name IN ('behavioral', 'capsules', 'overseer', 'security', 'analytics');")

if [ "$SCHEMA_COUNT" -eq 5 ]; then
    echo "✓ All 5 schemas created successfully"
else
    echo "✗ Schema verification failed. Expected 5 schemas, found $SCHEMA_COUNT"
    exit 1
fi

TABLE_COUNT=$(psql -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER -d $DATABASE_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema IN ('behavioral', 'capsules', 'overseer', 'security', 'analytics');")

echo "✓ Created $TABLE_COUNT tables across all schemas"

echo ""
echo "==============================================="
echo "Database initialization complete!"
echo "==============================================="
echo ""
echo "Connection string:"
echo "  postgresql://$DATABASE_USER:****@$DATABASE_HOST:$DATABASE_PORT/$DATABASE_NAME"
echo ""
echo "Next steps:"
echo "  1. Update application .env files with DATABASE_URL"
echo "  2. Start Redis: docker run -d -p 6379:6379 redis:7"
echo "  3. Test connection: make test-db"
echo ""
