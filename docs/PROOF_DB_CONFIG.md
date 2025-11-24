# Proof Database Configuration

## SQLite (default)
No configuration required. Files stored at `data/proofs.db` (or `PROOF_STORE_PATH` for JSONL fallback).

## Postgres
Set the following environment variables:

- `PROOF_BACKEND=postgres`
- `PROOF_DB_DSN=postgresql://user:password@host:port/database`

Requirements:
- `psycopg2` installed in the environment.
- Database reachable with create/update permissions for the `proofs` table.
