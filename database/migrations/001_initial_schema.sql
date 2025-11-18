-- Migration: 001_initial_schema
-- Description: Initial unified database schema
-- Created: Week 17 Day 1
-- Author: Claude (AI Agent)

-- This migration applies the unified schema
\i ../schema/unified_schema.sql

-- Record migration
INSERT INTO public.schema_migrations (version, description, applied_at)
VALUES ('001', 'Initial unified schema', NOW())
ON CONFLICT DO NOTHING;
