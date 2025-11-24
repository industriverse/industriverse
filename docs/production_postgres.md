# Production Postgres Setup

1. Install `psycopg2` in your environment.
2. Set environment variables:
   - `PROOF_BACKEND=postgres`
   - `PROOF_DB_DSN=postgresql://user:password@host:port/database`
3. Ensure the database user has create/update permissions.
4. Migrate proofs table (auto-created on first use). For HA, manage migrations via your preferred tool.
5. Validate connectivity:
   ```
   python - <<'PY'
   from src.proof_core.proof_hub.postgres_repository import PostgresProofRepository
   repo = PostgresProofRepository()
   print("Connected, table initialized.")
   PY
   ```
