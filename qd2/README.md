# Patient Data RAG System with Qdrant

A production-ready Retrieval-Augmented Generation (RAG) system for querying patient health data using Qdrant vector database, OpenAI embeddings, and FastAPI.

## 🎯 Features

- **Person-scoped isolation**: Strict `patient_id` filtering prevents cross-person data leakage
- **Multi-source data**: Profile, meals, fitness, and sleep data from Postgres and MongoDB
- **Time-based queries**: Natural language queries with date/time range filtering
- **Idempotent ingestion**: Stable point IDs enable safe re-ingestion
- **Metadata filtering**: Fast retrieval using indexed payload fields
- **LLM-powered answers**: GPT-4 generates grounded answers with citations

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Postgres   │──────▶│   FastAPI    │◀─────│   MongoDB   │
│  (Patients) │      │  Application │      │ (Health Data)│
└─────────────┘      └──────┬───────┘      └─────────────┘
                            │
                            │ Embed & Index
                            ▼
                     ┌──────────────┐
                     │    Qdrant    │
                     │ (Vector DB)  │
                     └──────┬───────┘
                            │
                            │ Vector Search
                            ▼
                     ┌──────────────┐
                     │  OpenAI LLM  │
                     │  (Answers)   │
                     └──────────────┘
```

## 📋 Prerequisites

- Python 3.10+
- Docker & Docker Compose
- OpenAI API key
- PostgreSQL (provided via Docker)
- MongoDB (provided via Docker)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd /path/to/qd2
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=people_data
QDRANT_VECTOR_SIZE=1536

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_LLM_MODEL=gpt-4o-mini
OPENAI_LLM_TEMPERATURE=0.1
OPENAI_LLM_MAX_TOKENS=1000

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=patient_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DB=patient_data

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development
EMBEDDING_BATCH_SIZE=64
INGEST_BATCH_SIZE=100
DEFAULT_TOP_K=10
MAX_TOP_K=50
```

### 3. Start Infrastructure

```bash
# Start Qdrant, PostgreSQL, and MongoDB
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 4. Run the Application

```bash
# Start FastAPI server
python main.py

# Server will start at http://localhost:8000
# Frontend UI: http://localhost:8000
# API docs: http://localhost:8000/docs
# API info: http://localhost:8000/api
```

**🎨 Frontend Interface Available!**

Open http://localhost:8000 in your browser for a beautiful web interface to:
- Ingest data with example templates
- Execute natural language queries with filters
- View results with evidence and metadata
- Monitor collection statistics

See [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) for detailed usage instructions.

### 5. Test the System

```bash
# Test ingestion
python test_ingestion.py

# Test queries (after ingestion)
python test_query.py
```

## 📊 Data Models

### Canonical Payload Structure

Every chunk in Qdrant follows this schema:

```json
{
  "patient_id": "uuid",
  "full_name": "string | null",
  "source": "profile | meals | fitness | sleep",
  "section": "summary | meal | recommendation | hour | ...",
  "report_type": "daily | weekly | monthly | null",
  "date": "YYYY-MM-DD | null",
  "start_ts": "int (UTC seconds) | null",
  "end_ts": "int (UTC seconds) | null",
  "text": "string"
}
```

### Chunking Strategy

| Source   | Chunks Created                                                     |
| -------- | ------------------------------------------------------------------ |
| Profile  | 1 summary per patient                                              |
| Meals    | 1 day summary + N meal chunks + 1 recommendation (if present)      |
| Fitness  | 1 summary per report (+ optional 24 hourly chunks)                 |
| Sleep    | 1 summary per report                                               |

## 🔌 API Endpoints

### Health & Info

- `GET /` - API information
- `GET /health` - Health check with Qdrant status
- `GET /collection/info` - Collection statistics

### Ingestion

- `POST /ingest/profile` - Ingest patient profiles
- `POST /ingest/meals` - Ingest meal reports
- `POST /ingest/fitness` - Ingest fitness reports
  - Query param: `include_hourly` (default: false)
- `POST /ingest/sleep` - Ingest sleep reports

### Query (RAG)

- `POST /query` - Execute RAG query

**Request:**
```json
{
  "person": "Raju Kumar",
  "question": "What did he eat on 2025-05-02?",
  "source": "meals",
  "from": "2025-05-02T00:00:00Z",
  "to": "2025-05-02T23:59:59Z",
  "top_k": 10
}
```

**Response:**
```json
{
  "answer": "LLM-generated answer...",
  "evidence": [
    {
      "score": 0.82,
      "payload": {"patient_id": "...", "source": "meals", "date": "2025-05-02"},
      "text": "Chunk content..."
    }
  ],
  "query_metadata": {
    "person": "Raju Kumar",
    "resolved_patient_id": "uuid",
    "results_count": 5
  }
}
```

### Management

- `DELETE /patient/{patient_id}` - Delete all data for a patient

## 💾 Data Ingestion

### Profile Data (from Postgres)

```python
import httpx

profiles = [
    {
        "patient_id": "00df6b5c-193b-47ce-a9b5-46d4975d9820",
        "first_name": "Vibha",
        "last_name": "Pai",
        "dob": "1992-05-28",
        "gender": "female",
        "height": 170.2,
        "waist": 106,
        "weight": 80,
        "email": "vibhapai92@gmail.com",
        "phone_number": "918296066561",
        "locale": "Asia/Kolkata",
        "created_at": "2025-06-27T08:39:07.107865Z",
        "profile_completion": {
            "basic": {"is_complete": True},
            "lifestyle": {"is_complete": False},
            "medical_history": {"is_complete": True}
        }
    }
]

response = httpx.post("http://localhost:8000/ingest/profile", json=profiles)
print(response.json())
```

### Meal Data (from MongoDB)

```python
meals = [
    {
        "patient_id": "7538e5a0-da8b-4745-95d5-ac1ceefd2c76",
        "report_type": "daily",
        "date": "2025-05-02",
        "meal_count": 3,
        "calories": 1850,
        "proteins": 95,
        "carbohydrates": 210,
        "fats": 65,
        "fiber": 28,
        "meals": [
            {
                "id": "meal-001",
                "name": "Breakfast",
                "time": "08:30:00",
                "items": [{"name": "Oatmeal", "quantity": "1 bowl"}],
                "total_macro_nutritional_value": {
                    "calories": 350,
                    "proteins": 12,
                    "carbohydrates": 65,
                    "fats": 8,
                    "fiber": 10
                }
            }
        ]
    }
]

response = httpx.post("http://localhost:8000/ingest/meals", json=meals)
```

See `test_data.py` for complete examples.

## 🔍 Query Examples

### 1. Meal Query with Time Filter

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "person": "Raju Kumar",
    "question": "What did Raju eat for breakfast on May 2nd?",
    "source": "meals",
    "from": "2025-05-02T00:00:00Z",
    "to": "2025-05-02T23:59:59Z",
    "top_k": 5
  }'
```

### 2. Fitness Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "person": "Raju Kumar",
    "question": "How many steps did Raju take and what was his activity level?",
    "source": "fitness",
    "from": "2025-05-02T00:00:00Z",
    "to": "2025-05-02T23:59:59Z"
  }'
```

### 3. Profile Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "person": "Vibha Pai",
    "question": "What is Vibha Pai'\''s height, weight, and BMI?",
    "source": "profile"
  }'
```

### 4. Cross-Source Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "person": "Raju Kumar",
    "question": "Summarize all health data for May 2nd, 2025",
    "from": "2025-05-02T00:00:00Z",
    "to": "2025-05-02T23:59:59Z",
    "top_k": 15
  }'
```

## 🔐 Security & Privacy

### PII Handling

- Email, phone, DOB stored in profile chunks (admin-only access recommended)
- Never log chunk text content in production
- Apply role-based access control before retrieval

### Patient Isolation

- **EVERY** query includes `patient_id` filter (enforced)
- No cross-person data leakage possible
- Person name resolution through Postgres lookup

## ⚙️ Configuration

### Embedding Model

Change in `.env`:
```
OPENAI_EMBEDDING_MODEL=text-embedding-3-large  # For better quality
QDRANT_VECTOR_SIZE=3072  # Must match model dimensions
```

### LLM Model

```
OPENAI_LLM_MODEL=gpt-4o  # For better reasoning
OPENAI_LLM_MAX_TOKENS=2000
```

### Performance Tuning

```
EMBEDDING_BATCH_SIZE=128  # Faster embedding (more API load)
INGEST_BATCH_SIZE=200     # Larger ingest batches
DEFAULT_TOP_K=15          # More evidence chunks
```

## 📈 Monitoring

### Logs

Structured JSON logs are written to stdout:

```json
{
  "event": "Generated embeddings",
  "batch_size": 64,
  "total_processed": 128,
  "timestamp": "2025-09-30T12:34:56.789012Z",
  "level": "info"
}
```

### Metrics

Key metrics to track:
- `ingest_docs_total` - Documents ingested per source
- `ingest_errors_total` - Failed ingestions
- `qdrant_upserts_total` - Points indexed
- `search_latency_ms` - Query latency
- `llm_tokens_total` - Token usage

## 🧪 Testing

### Unit Tests

```bash
pytest tests/
```

### Integration Tests

```bash
# 1. Start services
docker-compose up -d
python main.py

# 2. Run ingestion tests
python test_ingestion.py

# 3. Run query tests
python test_query.py
```

### Test Checklist

- [ ] Names normalized (trailing spaces removed)
- [ ] BMI computed correctly with outlier guards
- [ ] Timestamps converted to UTC seconds
- [ ] Point IDs stable (re-ingestion updates, not duplicates)
- [ ] Patient isolation enforced (every query filters by patient_id)
- [ ] Time-range filters work correctly
- [ ] LLM answers strictly from context

## 🐛 Troubleshooting

### Qdrant Connection Failed

```bash
# Check Qdrant is running
docker-compose ps qdrant

# Check logs
docker-compose logs qdrant

# Restart
docker-compose restart qdrant
```

### OpenAI API Errors

- Verify `OPENAI_API_KEY` is set correctly
- Check API quota/rate limits
- Reduce `EMBEDDING_BATCH_SIZE` for rate limit issues

### Empty Query Results

- Verify data is ingested: `GET /collection/info`
- Check person name spelling matches database
- Verify time range includes data
- Check logs for filter debugging

## 📚 Project Structure

```
qd2/
├── config.py                 # Configuration management
├── models.py                 # Pydantic models and schemas
├── utils.py                  # Utility functions (time, names, IDs)
├── chunkers.py               # Chunking logic per source
├── embedding_service.py      # OpenAI embedding generation
├── qdrant_client_wrapper.py  # Qdrant operations
├── llm_service.py            # LLM answer generation
├── ingestion.py              # Ingestion pipeline
├── retrieval.py              # RAG retrieval workflow
├── main.py                   # FastAPI application
├── test_data.py              # Sample test data
├── test_ingestion.py         # Ingestion tests
├── test_query.py             # Query tests
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Infrastructure setup
└── README.md                 # This file
```

## 🚢 Production Deployment

### Environment Variables

Externalize all config via environment variables (no `.env` file in production).

### Scaling

- Run multiple FastAPI workers: `uvicorn main:app --workers 4`
- Use managed Qdrant cluster for high availability
- Implement connection pooling for Postgres/MongoDB
- Add Redis for person-to-patient_id caching

### Security

- Enable HTTPS/TLS
- Add authentication middleware (JWT)
- Implement role-based access control per source
- Rotate API keys regularly
- Enable audit logging

### Backups

```bash
# Qdrant snapshots
docker exec qdrant /bin/sh -c "cd /qdrant/storage && tar -czf /backup/qdrant-$(date +%Y%m%d).tar.gz ."

# PostgreSQL
pg_dump -h localhost -U postgres patient_db > backup.sql

# MongoDB
mongodump --uri="mongodb://localhost:27017" --out=/backup/mongo
```

## 📝 License

Proprietary - All rights reserved

## 🤝 Contributing

Internal project - contact the team for contribution guidelines.

## 📧 Support

For issues or questions, contact the development team.

---

**Built with ❤️ for secure, scalable patient data RAG**

