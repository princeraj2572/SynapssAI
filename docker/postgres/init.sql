-- Enable pgvector extension for AI embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Confirm setup
SELECT 'pgvector ready' AS status;
