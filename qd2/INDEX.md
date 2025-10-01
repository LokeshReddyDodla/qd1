# Project Index

Quick reference guide to all files in the Patient Data RAG system.

## 📚 Documentation Files

| File                   | Purpose                                                  |
| ---------------------- | -------------------------------------------------------- |
| `README.md`            | Complete system documentation (start here)               |
| `QUICKSTART.md`        | 5-minute setup guide for getting started                 |
| `ARCHITECTURE.md`      | Detailed technical architecture and design decisions     |
| `PROJECT_SUMMARY.md`   | Executive overview and key features                      |
| `FRONTEND_GUIDE.md`    | Frontend user interface guide and tips                   |
| `INDEX.md`             | This file - navigation guide                             |

## 🔧 Core Application Files

| File                         | Purpose                                              | Lines |
| ---------------------------- | ---------------------------------------------------- | ----- |
| `main.py`                    | FastAPI application with all endpoints               | ~300  |
| `config.py`                  | Configuration management (env vars)                  | ~80   |
| `models.py`                  | Pydantic data models and schemas                     | ~200  |
| `utils.py`                   | Utility functions (time, names, health, IDs)         | ~250  |
| `chunkers.py`                | Chunking strategies for each data source             | ~400  |
| `embedding_service.py`       | OpenAI embedding generation                          | ~80   |
| `qdrant_client_wrapper.py`  | Qdrant operations (collection, search, upsert)       | ~200  |
| `llm_service.py`             | LLM answer generation with GPT-4                     | ~80   |
| `ingestion.py`               | Ingestion pipeline (validate, chunk, embed, upsert)  | ~300  |
| `retrieval.py`               | RAG retrieval workflow                               | ~200  |

**Total Core Code**: ~2,090 lines

## 🎨 Frontend & User Interface

| File                  | Purpose                                              |
| --------------------- | ---------------------------------------------------- |
| `frontend.html`       | Beautiful web UI for ingestion and queries           |
| `FRONTEND_GUIDE.md`   | Detailed guide for using the web interface           |

## 🧪 Testing & Examples

| File                  | Purpose                                              |
| --------------------- | ---------------------------------------------------- |
| `test_data.py`        | Sample patient data for testing                      |
| `test_ingestion.py`   | Integration tests for ingestion endpoints            |
| `test_query.py`       | Integration tests for RAG query functionality        |
| `setup_db.py`         | Script to populate databases with sample data        |
| `example_usage.py`    | Programmatic usage examples (non-HTTP)               |

## ⚙️ Configuration & Setup

| File                   | Purpose                                              |
| ---------------------- | ---------------------------------------------------- |
| `requirements.txt`     | Python dependencies                                  |
| `docker-compose.yml`   | Infrastructure setup (Qdrant, Postgres, MongoDB)     |
| `env_template.txt`     | Environment variable template                        |
| `Makefile`             | Convenience commands for development                 |
| `.gitignore`           | Git ignore rules                                     |

## 📂 Directories

| Directory    | Contents                                                      |
| ------------ | ------------------------------------------------------------- |
| `scripts/`   | Database initialization scripts                               |
| `qdrant_storage/` | Qdrant data (created automatically, gitignored)          |

## 🔍 Quick Navigation

### Getting Started
1. Read: `QUICKSTART.md` (5-minute setup)
2. Run: `make setup && make start && make run`
3. Open: http://localhost:8000 (web interface) or `make frontend`
4. Test: Use frontend UI or run `make test-ingest && make test-query`

### Understanding the System
1. Overview: `PROJECT_SUMMARY.md`
2. Full docs: `README.md`
3. Technical details: `ARCHITECTURE.md`

### Development Workflow
1. Configure: Edit `.env` (copy from `env_template.txt`)
2. Code: Modify core files (see table above)
3. Test: Run `test_*.py` scripts
4. Deploy: Follow production checklist in `README.md`

## 📖 Key Sections by File

### main.py
- FastAPI app initialization
- Health and info endpoints (`/`, `/health`, `/collection/info`)
- Ingestion endpoints (`/ingest/profile`, `/ingest/meals`, etc.)
- Query endpoint (`/query`)
- Management endpoints (`/patient/{id}`)

### models.py
- `ChunkPayload`: Canonical payload for Qdrant points
- `ProfileInput`, `MealInput`, `FitnessInput`, `SleepInput`: Input schemas
- `QueryRequest`, `QueryResponse`: RAG query interface
- `ProcessedChunk`, `IngestionError`: Internal models

### utils.py
- Time utilities: `parse_to_utc_seconds()`, `date_to_day_range()`
- Name utilities: `normalize_name()`, `build_full_name()`
- Health utilities: `calculate_bmi()`
- ID generators: `generate_profile_id()`, `generate_meal_id()`, etc.

### chunkers.py
- `chunk_profile()`: Profile → 1 summary chunk
- `chunk_meals()`: Meals → summary + meals + recommendations
- `chunk_fitness()`: Fitness → summary (+ optional hourly)
- `chunk_sleep()`: Sleep → 1 summary chunk

### ingestion.py
- `IngestionPipeline`: Orchestrates ingestion workflow
- `ingest_profiles()`, `ingest_meals()`, `ingest_fitness()`, `ingest_sleep()`
- Validation, chunking, embedding, upsert in batch

### retrieval.py
- `RetrievalService`: Orchestrates RAG query workflow
- `resolve_person_to_patient_id()`: Name → UUID lookup
- `query()`: Full RAG pipeline (resolve, filter, search, LLM)

### qdrant_client_wrapper.py
- `QdrantManager`: Wrapper for Qdrant operations
- `ensure_collection_exists()`, `create_payload_indexes()`
- `upsert_chunks()`, `search()`, `delete_by_patient()`

### embedding_service.py
- `EmbeddingService`: OpenAI embedding generation
- `embed_texts()`: Batch embedding with automatic batching
- `embed_single()`: Single text embedding

### llm_service.py
- `LLMService`: GPT-4 answer generation
- `generate_answer()`: Assemble context + prompt + LLM call
- System prompt with guardrails for grounded answers

## 🚀 Common Tasks

### Task: Add New Data Source

Files to modify:
1. `models.py`: Add `NewSourceInput` and update `Source` enum
2. `chunkers.py`: Add `chunk_new_source()` function
3. `ingestion.py`: Add `ingest_new_source()` method
4. `main.py`: Add `POST /ingest/new_source` endpoint
5. `test_data.py`: Add sample data
6. `test_ingestion.py`: Add test

### Task: Change Embedding Model

Files to modify:
1. `.env`: Update `OPENAI_EMBEDDING_MODEL` and `QDRANT_VECTOR_SIZE`
2. `config.py`: Update defaults if needed
3. Re-index all data (embeddings change)

### Task: Add Custom Metadata Field

Files to modify:
1. `models.py`: Add field to `ChunkPayload`
2. `chunkers.py`: Populate field in chunk functions
3. `qdrant_client_wrapper.py`: Add payload index if filterable
4. `retrieval.py`: Use field in filters if needed

### Task: Customize LLM Prompt

Files to modify:
1. `llm_service.py`: Edit `generate_answer()` system prompt
2. Test with `test_query.py`

### Task: Add Monitoring

Files to modify:
1. `main.py`: Add metrics middleware
2. All services: Emit metrics at key points
3. Deploy: Configure metrics collector (Prometheus, etc.)

## 📊 Code Statistics

| Category              | Files | Lines  | Purpose                       |
| --------------------- | ----- | ------ | ----------------------------- |
| Core Application      | 10    | ~2,090 | Main business logic           |
| Frontend              | 1     | ~720   | Web UI interface              |
| Tests & Examples      | 5     | ~800   | Validation and examples       |
| Documentation         | 6     | ~3,500 | Guides and references         |
| Configuration         | 5     | ~200   | Setup and dependencies        |
| **Total**             | **27**| **~7,310** | **Complete system**       |

## 🔗 External Dependencies

### Python Packages
- **FastAPI**: Web framework
- **Pydantic**: Data validation
- **Qdrant Client**: Vector database
- **OpenAI**: Embeddings and LLM
- **Psycopg2**: Postgres connector
- **PyMongo**: MongoDB connector
- **Structlog**: Structured logging

### Infrastructure
- **Qdrant**: Vector database (Docker)
- **PostgreSQL**: Patient profiles (Docker)
- **MongoDB**: Health data (Docker)

### External APIs
- **OpenAI API**: Embeddings and LLM (requires API key)

## 📞 Support

- **Documentation Issues**: Check README.md and ARCHITECTURE.md
- **Setup Issues**: See QUICKSTART.md troubleshooting section
- **Code Questions**: Read inline comments in source files
- **Production Deployment**: Follow checklist in PROJECT_SUMMARY.md

## 🎯 Next Steps

1. **First Time Here?** → Read `QUICKSTART.md`
2. **Want Details?** → Read `README.md`
3. **Need Architecture?** → Read `ARCHITECTURE.md`
4. **Ready to Code?** → Start with `example_usage.py`
5. **Deploying?** → Check `PROJECT_SUMMARY.md` production section

---

**Index Version**: 1.0
**Last Updated**: 2025-09-30
**Project**: Patient Data RAG System

