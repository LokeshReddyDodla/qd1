# System Architecture

Detailed architecture documentation for the Patient Data RAG system.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        External Data Sources                        │
├──────────────────────────────┬──────────────────────────────────────┤
│         PostgreSQL           │            MongoDB                   │
│    (Patient Profiles)        │      (Health Data: Meals,            │
│                              │       Fitness, Sleep)                │
└──────────────┬───────────────┴─────────┬────────────────────────────┘
               │                         │
               │                         │
               ▼                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                         │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Ingestion   │  │  Retrieval   │  │  Management  │             │
│  │  Endpoints   │  │  Endpoint    │  │  Endpoints   │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                  │                  │                     │
│  ┌──────▼──────────────────▼──────────────────▼───────┐            │
│  │           Ingestion Pipeline                        │            │
│  │  - Validation                                       │            │
│  │  - Normalization (names, times, BMI)               │            │
│  │  - Chunking (per source strategy)                  │            │
│  │  - Stable ID generation                            │            │
│  └──────┬──────────────────────────────────┬──────────┘            │
│         │                                   │                       │
│  ┌──────▼────────┐                  ┌──────▼──────────┐            │
│  │  Embedding    │                  │   Retrieval     │            │
│  │  Service      │                  │   Service       │            │
│  │  (OpenAI)     │                  │  - Name resolve │            │
│  └──────┬────────┘                  │  - Filter build │            │
│         │                            │  - Vector search│            │
│         │                            └──────┬──────────┘            │
└─────────┼───────────────────────────────────┼──────────────────────┘
          │                                    │
          ▼                                    ▼
┌─────────────────────┐            ┌─────────────────────┐
│  Qdrant Vector DB   │◀───────────│   LLM Service       │
│  - Collection       │            │   (GPT-4)           │
│  - Payload Indexes  │            │   - Answer gen      │
│  - HNSW Index       │            │   - Context grounding│
└─────────────────────┘            └─────────────────────┘
```

## Core Components

### 1. Data Models (`models.py`)

**Purpose**: Type-safe data contracts for all system components.

**Key Models**:
- `ChunkPayload`: Canonical payload structure stored in Qdrant
- `ProfileInput`, `MealInput`, `FitnessInput`, `SleepInput`: Input schemas
- `QueryRequest`, `QueryResponse`: RAG query interface
- `ProcessedChunk`: Internal representation with embeddings

**Design Principles**:
- Strict validation using Pydantic
- Enum types for source, section, report_type
- Optional fields with clear semantics

### 2. Utilities (`utils.py`)

**Time Normalization**:
- `parse_to_utc_seconds()`: Converts any datetime format to UTC epoch seconds
- `date_to_day_range()`: Creates 00:00:00-23:59:59 timestamp ranges
- Handles MongoDB date objects (`{"$date": "..."}`)

**Name Processing**:
- `normalize_name()`: Strips whitespace, handles None
- `build_full_name()`: Combines first/last names

**Health Metrics**:
- `calculate_bmi()`: BMI with outlier guards (height: 50-250cm, weight: 2-500kg)

**ID Generation**:
- Stable, deterministic IDs for idempotent upserts
- Format: `{source}:{patient_id}:{type-specific-parts}`
- Examples:
  - `profile:uuid`
  - `meals:uuid:2025-05-02:meal:meal-id`
  - `fitness:uuid:daily:1714608000:summary`

### 3. Chunking Strategies (`chunkers.py`)

**Profile Chunking**:
```python
Input: ProfileInput
Output: 1 summary chunk
Content: Patient demographics, anthropometrics, BMI, contacts, completion status
```

**Meal Chunking**:
```python
Input: MealInput
Output: 
  - 1 day summary (total macros)
  - N meal chunks (one per meal with items, macros, micros, feedback)
  - 1 recommendation chunk (target macros)
```

**Fitness Chunking**:
```python
Input: FitnessInput
Output:
  - 1 summary (steps, active duration, peak hour, distribution)
  - Optional: 24 hourly chunks (disabled by default)
```

**Sleep Chunking**:
```python
Input: SleepInput
Output: 1 summary (quality, deep%, REM%, awake%)
Special: Explicit "no data" text when all zeros
```

**Design Decisions**:
- Separate chunks for semantic coherence
- Human-readable text with units
- Metadata preserved for filtering
- Chunk size: ~350-800 tokens

### 4. Qdrant Manager (`qdrant_client_wrapper.py`)

**Responsibilities**:
- Collection lifecycle (create, ensure exists)
- Payload index creation (patient_id, source, date, timestamps)
- Point upsert (idempotent)
- Filtered vector search
- Collection statistics

**Collection Schema**:
```python
{
  "vectors": {
    "size": 1536,  # text-embedding-3-small
    "distance": "COSINE"
  },
  "payload_indexes": {
    "patient_id": "keyword",
    "source": "keyword",
    "report_type": "keyword",
    "date": "keyword",
    "section": "keyword",
    "start_ts": "integer",
    "end_ts": "integer"
  }
}
```

**Search Flow**:
1. Build filter (MUST conditions for patient_id, optional source/time)
2. Execute vector search with filter
3. Return scored results with payloads

### 5. Embedding Service (`embedding_service.py`)

**Features**:
- Automatic batching (configurable batch size)
- Retry/backoff (handled by OpenAI SDK)
- Model: `text-embedding-3-small` (1536 dims) by default

**Performance**:
- Batches of 64 texts per API call
- Parallel processing for large ingests

### 6. Ingestion Pipeline (`ingestion.py`)

**Workflow**:
```
Input Docs → Validate → Chunk → Embed → Upsert → Response
              ↓          ↓       ↓       ↓
           Errors    Errors  Errors  Success
```

**Per-Source Processing**:
1. Validate patient_id (UUID format)
2. Call source-specific chunker
3. Collect all chunks
4. Batch embed all texts
5. Attach vectors to chunks
6. Upsert to Qdrant with stable IDs

**Error Handling**:
- Document-level errors don't block batch
- Errors collected with doc_index and reason
- Returned in response for client inspection

### 7. Retrieval Service (`retrieval.py`)

**Query Workflow**:
```
Query → Resolve Name → Build Filter → Embed Query → 
  → Vector Search → Format Evidence → LLM Answer → Response
```

**Name Resolution**:
1. Check if input is UUID (return as-is)
2. Query Postgres: `LOWER(first_name || ' ' || last_name) = query`
3. Fallback: partial match on first or last name
4. Cache in Redis (future optimization)

**Filter Construction**:
```python
must: [
  patient_id = resolved_id,  # Always required
  source = filter_source,    # Optional
  start_ts >= from,          # Optional time range
  end_ts <= to               # Optional time range
]
```

**Evidence Formatting**:
- Score + payload + text
- Sorted by relevance score
- Limited to top_k results

### 8. LLM Service (`llm_service.py`)

**Answer Generation**:
```
Evidence Chunks → Context Assembly → System Prompt + User Question → 
  → GPT-4 → Grounded Answer
```

**System Prompt Guardrails**:
1. Answer STRICTLY from evidence
2. Say "I don't have that data" when insufficient
3. Include dates and units
4. Be concise and precise
5. Acknowledge conflicts if present

**Configuration**:
- Model: `gpt-4o-mini` (fast, cheap) or `gpt-4o` (better reasoning)
- Temperature: 0.1 (focused)
- Max tokens: 1000 (configurable)

### 9. FastAPI Application (`main.py`)

**Endpoints**:

| Method | Path                | Purpose                              |
| ------ | ------------------- | ------------------------------------ |
| GET    | `/`                 | API info                             |
| GET    | `/health`           | Health check with Qdrant status      |
| GET    | `/collection/info`  | Collection statistics                |
| POST   | `/ingest/profile`   | Ingest patient profiles              |
| POST   | `/ingest/meals`     | Ingest meal reports                  |
| POST   | `/ingest/fitness`   | Ingest fitness reports               |
| POST   | `/ingest/sleep`     | Ingest sleep reports                 |
| POST   | `/query`            | RAG query execution                  |
| DELETE | `/patient/{id}`     | Delete all patient data              |

**Middleware**:
- CORS (configurable origins)
- Structured logging (JSON format)

**Service Initialization**:
- Lazy initialization on first request
- Singleton pattern for service instances
- Collection and indexes created automatically

## Data Flow

### Ingestion Flow

```
1. Client sends JSON array of documents
   ↓
2. FastAPI endpoint receives and validates schema
   ↓
3. IngestionPipeline processes batch:
   a. Validate patient_id (UUID format)
   b. Call source-specific chunker
   c. Generate stable point IDs
   d. Collect chunks with payloads
   ↓
4. EmbeddingService:
   a. Extract text from all chunks
   b. Batch embed (64 texts per API call)
   c. Return vectors in order
   ↓
5. QdrantManager:
   a. Create PointStruct with id, vector, payload
   b. Upsert to collection (replaces if ID exists)
   ↓
6. Return IngestResponse:
   - accepted: docs processed successfully
   - indexed_points: total chunks created
   - errors: list of failures with reasons
```

### Query Flow

```
1. Client sends QueryRequest:
   - person: name or UUID
   - question: natural language query
   - source: optional filter (meals/fitness/sleep/profile)
   - time range: optional from/to
   - top_k: number of results
   ↓
2. RetrievalService.resolve_person_to_patient_id():
   a. Check if input is UUID
   b. Else query Postgres by name (case-insensitive)
   c. Return patient_id or None
   ↓
3. Build metadata filter:
   must: [patient_id = resolved_id]
   optional: source, time range
   ↓
4. EmbeddingService.embed_single(question)
   ↓
5. QdrantManager.search():
   a. Execute vector search with filter
   b. Return top_k results with scores and payloads
   ↓
6. Format evidence items
   ↓
7. LLMService.generate_answer():
   a. Assemble context from evidence texts
   b. Build system prompt with guardrails
   c. Call GPT-4 with context + question
   d. Return grounded answer
   ↓
8. Return QueryResponse:
   - answer: LLM-generated text
   - evidence: list of chunks with scores
   - query_metadata: resolved IDs, filters applied
```

## Security Architecture

### Patient Data Isolation

**Guarantees**:
1. Every retrieval query MUST include `patient_id` filter
2. No cross-patient data leakage possible
3. Name resolution through controlled Postgres lookup

**Implementation**:
```python
# In QdrantManager.search()
must_conditions = [
    FieldCondition(
        key="patient_id",
        match=MatchValue(value=patient_id)  # Always required
    )
]
```

### PII Handling

**Profile Data**:
- Email, phone, DOB stored in profile chunks
- Recommendation: Apply role-based access before retrieval
- Option: Exclude PII from embeddings (keep in payload only)

**Logging**:
- Never log chunk text content in production
- Log only metadata: patient_id, counts, timings
- Use structured logging for security audits

### Access Control (Future)

```python
# Recommended middleware
@app.middleware("http")
async def check_access(request: Request, call_next):
    user = authenticate(request)
    allowed_sources = get_user_sources(user)
    # Enforce source ACLs
    return await call_next(request)
```

## Performance Considerations

### Indexing

**Payload Indexes**:
- `patient_id`: Fast filtering (most queries)
- `source`: Source-scoped queries
- `start_ts`, `end_ts`: Range queries for time filters
- `date`: Exact date lookups

**Impact**: 10-100x speedup on filtered queries

### Embedding Batching

**Strategy**:
- Batch size: 64 (configurable)
- Parallel API calls for large ingests
- Trade-off: API rate limits vs. throughput

**Example**:
```python
# 1000 chunks
# Without batching: 1000 API calls (~10 min)
# With batching (64): 16 API calls (~10 sec)
```

### Vector Search

**HNSW Parameters** (Qdrant defaults):
- `m`: 16 (connections per node)
- `ef_construct`: 100 (build-time quality)
- `ef_search`: 64 (query-time quality)

**Tune for**:
- Higher `ef_search` → better recall, slower queries
- Lower `ef_search` → faster queries, lower recall

### Chunk Volume Control

**Without hourly fitness chunks**:
- ~10 chunks per patient-day

**With hourly fitness chunks**:
- ~34 chunks per patient-day

**Recommendation**: Disable hourly chunks unless hour-level queries required

## Scalability

### Current Limits

- **Points**: 200K+ on single Qdrant instance
- **Throughput**: ~100 ingests/sec, ~50 queries/sec
- **Latency**: <100ms vector search, ~1-2s end-to-end query

### Scaling Strategies

**Horizontal (Qdrant)**:
- Qdrant cluster with sharding
- Replicas for read scaling

**Horizontal (API)**:
- Multiple FastAPI workers (`--workers 4`)
- Load balancer (nginx, ALB)

**Vertical**:
- More RAM for Qdrant (HNSW index in-memory)
- GPU for embeddings (local model)

**Caching**:
- Redis for name → patient_id mapping
- Response cache for common queries

## Failure Modes

### Embedding API Failure

**Symptoms**: Ingestion fails, returns errors
**Mitigation**:
- Retry with exponential backoff (built into OpenAI SDK)
- Dead-letter queue for failed batches
- Switch to local embedding model

### Qdrant Unavailable

**Symptoms**: Health check fails, queries error
**Mitigation**:
- Health check before ingestion
- Retry logic with circuit breaker
- Persistent volume for data recovery

### Invalid Timestamps

**Symptoms**: Chunks skipped, date filters fail
**Mitigation**:
- Strict validation in `parse_to_utc_seconds()`
- Fallback to date-only if timestamps invalid
- Log warnings for investigation

### Name Resolution Fails

**Symptoms**: Query returns "person not found"
**Mitigation**:
- Support patient_id input directly
- Fuzzy name matching (Levenshtein distance)
- Suggest similar names in error response

## Monitoring Points

### Key Metrics

| Metric                    | Type      | Alert Threshold     |
| ------------------------- | --------- | ------------------- |
| `ingest_docs_total`       | Counter   | N/A                 |
| `ingest_errors_total`     | Counter   | > 5% of ingests     |
| `qdrant_upserts_total`    | Counter   | N/A                 |
| `search_latency_ms`       | Histogram | p95 > 200ms         |
| `llm_tokens_total`        | Counter   | Track cost          |
| `embedding_api_errors`    | Counter   | > 1% of calls       |
| `query_zero_results_rate` | Gauge     | > 20%               |

### Health Checks

- Qdrant connection: `GET /health`
- Collection exists and has points: `GET /collection/info`
- Postgres connection: Test name resolution
- OpenAI API: Test embedding generation

### Logs to Monitor

- Ingestion errors (patient_id, reason)
- Query zero-results (person, filters)
- Embedding API failures (rate limits, errors)
- Outlier data (BMI computation skipped)

---

**Architecture Version**: 1.0
**Last Updated**: 2025-09-30

