# Database Schema Notes

This schema is designed for a local-first MVP that still preserves the boundaries needed for scale.

## Design choices

- `SQLite` remains the main metadata store.
- Raw and normalized source payloads are stored on disk, with paths referenced from `documents`.
- Embeddings are stored in a local vector index on disk. SQLite stores collection metadata and entity-to-vector mappings.
- `pipeline_runs` and `model_registry_entries` make AI output reproducible.
- `jobs` and `job_events` support async workflows without requiring Redis or a distributed queue.

## Key entity groups

### Ingestion and documents

- `sources`
- `source_checkpoints`
- `documents`
- `document_fingerprints`
- `document_chunks`

### Async jobs and lineage

- `jobs`
- `job_events`
- `pipeline_runs`
- `run_artifacts`
- `extraction_runs`

### Research artifacts

- `problems`
- `problem_clusters`
- `problem_cluster_memberships`
- `ideas`
- `idea_scores`
- `idea_evidence`
- `reports`

### AI configuration

- `model_registry_entries`
- `prompt_versions`

### Vector search

- `vector_collections`
- `vector_entries`
- `vector_sync_runs`

## Practical MVP interpretation

The MVP can start with:

1. one worker process
2. one source connector
3. one embedding model
4. one vector collection for document chunks
5. one active default model per task

The schema already supports expansion without requiring another migration just to introduce lineage or traceability later.
