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

### 🌟 **NEW!** Railway Deployment (Production-Ready in 10 Minutes!) 🚂

**Deploy your entire system to the cloud with automatic HTTPS and monitoring:**

```bash
# 1. Create Qdrant Cloud cluster (2 min)
# - Go to https://cloud.qdrant.io/
# - Create free cluster, copy URL and API key

# 2. Push to GitHub (1 min)
git add .
git commit -m "Deploy to Railway"
git push origin main

# 3. Deploy to Railway (1 min)
# - Go to https://railway.app/new
# - Deploy from GitHub repo
# - Add environment variables (see .env.railway)

# 4. Done! Your app is live at:
# https://your-app.up.railway.app
```

✅ **Fully managed** - Zero infrastructure to maintain  
✅ **Auto-deploy** - Push to GitHub, auto-deploys  
✅ **HTTPS included** - Automatic SSL certificates  
✅ **Custom domains** - Add your own domain easily  
✅ **One-click scaling** - Scale up when needed  
✅ **$5/month** - Affordable production hosting  

📖 **Complete Railway guide**: [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)  
🔧 **Environment variables**: [.env.railway](.env.railway)

---

### Option A: Qdrant Cloud (Recommended for Local Development) ☁️

**Production-ready local setup in 5 minutes with zero infrastructure management:**

```bash
# 1. Create free cluster at https://cloud.qdrant.io/
# - 1 GB RAM, 4 GB disk - FREE!
# - Automatic backups, HA, monitoring included
# - Copy cluster URL and API key

# 2. Configure environment
cp .env.docker .env
nano .env

# Add these to .env:
QDRANT_HOST=your-cluster.aws.cloud.qdrant.io
QDRANT_API_KEY=your-api-key-from-dashboard
QDRANT_USE_HTTPS=true
OPENAI_API_KEY=your-openai-key

# 3. Start application
python main.py

# 4. Access at http://localhost:1531
```

✅ **Zero maintenance** - Fully managed  
✅ **Automatic backups** - Never lose data  
✅ **Production-ready** - HA, monitoring, security  
✅ **Free tier** - Perfect for development  
✅ **Scales with a click** - When you need more  

📖 **Complete guide**: [QDRANT_CLOUD_GUIDE.md](QDRANT_CLOUD_GUIDE.md)

---

### Option B: Docker Deployment (For Full Control) 🐳

**Complete deployment with one command:**

```bash
# 1. Set your API key
cp .env.docker .env
# Edit .env and add your OPENAI_API_KEY

# 2. Start everything (app + databases)
./docker-start.sh

# Or use make commands
make docker-up

# Access at: http://localhost:1531
```

**All services run in Docker containers with:**
- ✅ Automatic health checks
- ✅ Persistent data volumes
- ✅ Isolated networking
- ✅ Auto-restart on failure

📖 **See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for complete Docker guide**  
📋 **See [DOCKER_QUICK_REF.md](DOCKER_QUICK_REF.md) for command reference**

---

### Option C: Local Development 💻

**For development with local Python:**

```bash
cd /path/to/qd2
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
# Copy from template
cp env_template.txt .env
```

Edit `.env` with your settings:

```bash
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=people_data

# Other services (defaults work for Docker setup)
POSTGRES_HOST=localhost
MONGO_URI=mongodb://localhost:27017
```

### 3. Start Infrastructure (Databases Only)

```bash
# Start only Qdrant, PostgreSQL, and MongoDB
make start
# Or: docker-compose up -d qdrant postgres mongodb

# Verify services are running
docker-compose ps
```

### 4. Run the Application Locally

```bash
# Start FastAPI server (local Python)
python main.py

# Or use make
make run

# Server will start at http://localhost:1531
# Frontend UI: http://localhost:1531
# API docs: http://localhost:1531/docs
```

**🎨 Frontend Interface Available!**

Open http://localhost:1531 in your browser for a beautiful web interface to:
- Ingest data with example templates (Profile, Meals, Fitness, Sleep, CGM)
- Execute natural language queries with filters
- View results with evidence and metadata
- Monitor collection statistics

See [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) for detailed usage instructions.

---

## 🐳 Docker Deployment Details

### All Services in Docker

```bash
# Start everything (recommended for production)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app

# Stop everything
docker-compose down
```

### Individual Service Control

```bash
# Restart app only
docker-compose restart app

# Rebuild after code changes
docker-compose build app
docker-compose up -d app

# Shell into container
docker-compose exec app bash

# Run diagnostic script
docker-compose exec app python check_patient_data.py <patient_id>
```

### Data Persistence

All data persists in Docker volumes:
- `qdrant_storage` - Vector embeddings
- `postgres_data` - Patient metadata
- `mongo_data` - Source documents

```bash
# Backup volumes
docker run --rm -v qd2_qdrant_storage:/source -v $(pwd)/backups:/backup \
  alpine tar czf /backup/qdrant-backup.tar.gz -C /source .

# List volumes
docker volume ls | grep qd2
```

---

## 🎯 Using Make Commands

```bash
# Local development
make setup          # Install dependencies
make start          # Start databases only
make run            # Run app locally
make stop           # Stop databases

# Docker deployment  
make docker-up      # Start all services
make docker-down    # Stop all services
make docker-logs    # View logs
make docker-rebuild # Rebuild app
make docker-status  # Show status

# Development
make test           # Run tests
make frontend       # Open in browser
```

---

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

