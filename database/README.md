# Industriverse Database

**Week 17: Unified Database Setup**

This directory contains the unified database schema, configuration, and migration scripts for the Industriverse platform.

## 📋 Overview

The Industriverse database consolidates:
- **Week 9**: Behavioral Tracking Infrastructure
- **Week 16**: Capsule-Pins PWA (sensor data, capsules, consensus)
- **Main Framework**: 10-layer architecture requirements

## 🗄️ Database Structure

### Schemas

| Schema | Purpose | Tables |
|--------|---------|--------|
| `behavioral` | User behavioral tracking and analytics | 6 |
| `capsules` | Capsule management and sensor data | 3 |
| `overseer` | System governance and health metrics | 3 |
| `security` | Authentication, authorization, audit | 3 |
| `analytics` | Aggregated analytics and reporting | 1 |

### Key Tables

**Behavioral Schema:**
- `interaction_events` - User interaction events
- `user_sessions` - Session tracking
- `behavioral_vectors` - Computed behavioral profiles
- `bv_history` - Behavioral vector history
- `user_archetypes` - Behavioral personas
- `ux_experiments` - A/B testing experiments

**Capsules Schema:**
- `capsules` - Main capsule entities
- `capsule_rules` - Automated capsule creation rules
- `sensor_readings` - Raw sensor data (partitioned)

**Overseer Schema:**
- `governance_policies` - Capsule governance rules
- `capsule_events` - Capsule audit trail
- `system_health_metrics` - System performance metrics

**Security Schema:**
- `users` - User accounts
- `api_keys` - API key management
- `audit_logs` - Security audit trail

**Analytics Schema:**
- `capsule_analytics` - Aggregated capsule statistics

## 🚀 Quick Start

### Prerequisites

- PostgreSQL 16+
- Redis 7+
- `psql` command-line tool
- `make` (optional, for shortcuts)

### 1. Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```bash
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=industriverse
DATABASE_USER=industriverse
DATABASE_PASSWORD=your_secure_password
REDIS_URL=redis://localhost:6379/0
```

### 2. Initialize Database

**Option A: Using Make (recommended)**

```bash
make init
```

**Option B: Manual**

```bash
cd scripts
chmod +x init_db.sh
./init_db.sh
```

### 3. Verify Installation

```bash
make test-connection
```

Expected output:
```
PostgreSQL 16.x
PONG
```

## 📦 Using Docker (Development)

For local development, you can use Docker Compose:

```bash
# Start PostgreSQL and Redis
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

## 🔄 Migrations

Migrations are stored in `migrations/` directory.

### Apply Migrations

```bash
make migrate
```

### Create New Migration

1. Create a new file: `migrations/XXX_description.sql`
2. Write SQL statements
3. Run `make migrate`

Example migration:

```sql
-- Migration: 002_add_tenant_support
-- Description: Add multi-tenant support
-- Created: Week 17 Day X

ALTER TABLE capsules.capsules ADD COLUMN tenant_id UUID;
CREATE INDEX idx_capsules_tenant_id ON capsules.capsules(tenant_id);
```

## 🌱 Seed Data

To populate the database with test data:

```bash
make seed
```

This will insert sample:
- Users
- Capsules
- Sensor readings
- Behavioral events

## 💾 Backup & Restore

### Create Backup

```bash
make backup
```

Backups are stored in `backups/industriverse_YYYYMMDD_HHMMSS.sql`

### Restore from Backup

```bash
make restore
```

Follow the prompts to select a backup file.

## 🔍 Querying the Database

### Active Capsules

```sql
SELECT * FROM capsules.active_capsules
WHERE severity = 'critical'
ORDER BY created_at DESC
LIMIT 10;
```

### User Engagement

```sql
SELECT * FROM behavioral.user_engagement_summary
WHERE engagement_score::float > 0.7;
```

### System Health

```sql
SELECT * FROM overseer.system_health_dashboard
WHERE component_name = 'capsule_creation_engine';
```

## 🔧 Maintenance

### Reset Database (⚠️ Destructive)

```bash
make reset
```

This will:
1. Drop existing database
2. Recreate from schema
3. Apply all migrations

### Clean Backups

```bash
make clean
```

## 📊 Performance Tuning

### Indexes

All critical columns have indexes:
- Foreign keys
- Frequently queried columns
- JSONB columns (GIN indexes)

### Partitioning

`sensor_readings` table is partitioned by month for better performance with large datasets.

To add new partitions:

```sql
CREATE TABLE sensor_readings_2025_12 PARTITION OF capsules.sensor_readings
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');
```

### Connection Pooling

Recommended connection pool settings (in `config/database.yaml`):

```yaml
pool:
  min_connections: 5
  max_connections: 20
  connection_timeout: 30
```

## 🔐 Security

### Production Checklist

- [ ] Change default passwords in `.env`
- [ ] Enable SSL for PostgreSQL connections
- [ ] Set `DATABASE_SSL_MODE=require`
- [ ] Restrict database user permissions
- [ ] Enable audit logging
- [ ] Set up read replicas for high availability
- [ ] Configure backup encryption
- [ ] Implement connection rate limiting

### SSL Configuration

For production, configure SSL in `.env`:

```bash
DATABASE_SSL_MODE=verify-full
DATABASE_SSL_CERT=/path/to/client-cert.pem
DATABASE_SSL_KEY=/path/to/client-key.pem
DATABASE_SSL_ROOT_CERT=/path/to/ca-cert.pem
```

## 🐛 Troubleshooting

### Connection Refused

```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check PostgreSQL logs
tail -f /var/log/postgresql/postgresql-16-main.log
```

### Permission Denied

```bash
# Grant superuser privileges
psql -U postgres -c "ALTER USER industriverse WITH SUPERUSER;"
```

### Migration Failed

```bash
# Check migration status
psql $DATABASE_URL -c "SELECT * FROM public.schema_migrations ORDER BY applied_at DESC;"

# Manually revert migration
psql $DATABASE_URL -c "DELETE FROM public.schema_migrations WHERE version = 'XXX';"
```

## 📚 Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/16/)
- [Redis Documentation](https://redis.io/documentation)
- [Industriverse Database Schema](./schema/unified_schema.sql)
- [Database Configuration](./config/database.yaml)

## 🤝 Contributing

When making database changes:

1. Create a new migration file
2. Test locally with `make reset && make migrate`
3. Update this README if adding new tables/schemas
4. Commit migration files with descriptive messages

## 📝 Changelog

### Week 17 Day 1 (2025-11-18)
- ✅ Created unified database schema
- ✅ Consolidated Week 9 behavioral tracking tables
- ✅ Integrated Week 16 capsule tables
- ✅ Added overseer, security, analytics schemas
- ✅ Created initialization scripts
- ✅ Added Makefile for operations
- ✅ Documented setup and usage

## 📧 Support

For database-related issues, please refer to:
- [Comprehensive Enhancement Analysis](../COMPREHENSIVE_ENHANCEMENT_ANALYSIS.md)
- [Week 17 Development Log](../docs/week17_development_log.md)
