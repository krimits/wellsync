-- Migration: Add pgvector extension and knowledge_chunks table
-- Run once against the WellSync PostgreSQL database.
--
-- Prerequisites:
--   Docker image: pgvector/pgvector:pg16 (replaces postgres:16 in docker-compose.yml)
--
-- Usage:
--   psql $DATABASE_URL -f migrations/add_knowledge_chunks.sql
--
-- After this migration, run the ingestion script:
--   python -m src.knowledge.ingest

-- Enable the pgvector extension (idempotent)
CREATE EXTENSION IF NOT EXISTS vector;

-- Knowledge base table: curated wellness guideline chunks
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id          SERIAL PRIMARY KEY,
    category    TEXT NOT NULL CHECK (category IN ('sleep', 'exercise', 'nutrition', 'stress')),
    content     TEXT NOT NULL,
    embedding   vector(384),    -- sentence-transformers/all-MiniLM-L6-v2 output dimension
    source      TEXT            -- bibliographic reference (e.g. 'ACSM 2024')
);

-- IVFFlat index for fast approximate cosine similarity search
-- lists=10 is appropriate for a corpus of ~30 rows; increase to 100 for larger corpora.
CREATE INDEX IF NOT EXISTS knowledge_chunks_embedding_idx
    ON knowledge_chunks
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);
