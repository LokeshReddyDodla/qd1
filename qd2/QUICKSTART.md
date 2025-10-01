# Quick Start Guide

Get the RAG system running in 5 minutes.

## Step 1: Install Dependencies

```bash
make setup
# or manually:
pip install -r requirements.txt
```

## Step 2: Configure OpenAI API Key

Edit `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-key-here
```

Get your key from: https://platform.openai.com/api-keys

## Step 3: Start Services

```bash
make start
# or manually:
docker-compose up -d
```

This starts:
- Qdrant (vector database) on port 6333
- PostgreSQL on port 5432
- MongoDB on port 27017

## Step 4: Populate Sample Data (Optional)

```bash
make setup-db
# or manually:
python setup_db.py
```

This adds:
- 2 patient profiles to Postgres
- Sample meals, fitness, and sleep data to MongoDB

## Step 5: Run the Application

```bash
make run
# or manually:
python main.py
```

The API will be available at:
- **Frontend UI**: http://localhost:8000 ⭐ **Use this for easy interaction!**
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 5.1. Using the Frontend (Recommended)

Open your browser to http://localhost:8000 for a beautiful web interface:

```bash
# Auto-open browser
make frontend

# Or manually navigate to http://localhost:8000
```

The frontend provides:
- 📥 Easy data ingestion with example templates
- 🔍 Natural language queries with filters
- 📊 Real-time collection statistics
- ✅ Visual feedback for all operations

See [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) for detailed instructions.

### 5.2. Using the API Directly (Command Line)

## Step 6: Ingest Data

```bash
make test-ingest
# or manually:
python test_ingestion.py
```

This will:
1. Index patient profiles
2. Index meal data
3. Index fitness data
4. Index sleep data

Expected output:
```
✓ Health Check: PASS
✓ Profile Ingestion: PASS
✓ Meals Ingestion: PASS
✓ Fitness Ingestion: PASS
✓ Sleep Ingestion: PASS
✓ Collection Info: PASS

Passed: 6/6
```

## Step 7: Query the System

```bash
make test-query
# or manually:
python test_query.py
```

Or use curl:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "person": "Raju Kumar",
    "question": "What did Raju eat on 2025-05-02?",
    "source": "meals",
    "from": "2025-05-02T00:00:00Z",
    "to": "2025-05-02T23:59:59Z",
    "top_k": 10
  }'
```

## Interactive API Docs

Open http://localhost:8000/docs in your browser to:
- Browse all endpoints
- Test queries interactively
- View request/response schemas

## Troubleshooting

### Services won't start

```bash
# Check Docker is running
docker --version

# View logs
make logs
```

### OpenAI API errors

- Check your API key in `.env`
- Verify you have credits: https://platform.openai.com/account/usage

### Empty query results

```bash
# Check collection has data
curl http://localhost:8000/collection/info

# If points_count is 0, run ingestion again
python test_ingestion.py
```

## Next Steps

1. **Add your own data**: Use the `/ingest/*` endpoints with your data
2. **Customize chunking**: Edit `chunkers.py` for your use case
3. **Tune retrieval**: Adjust `top_k`, try different `source` filters
4. **Monitor**: Check structured logs for debugging

## Stopping the System

```bash
# Stop services
make stop

# Remove containers
make clean

# Remove everything including data
make clean-all
```

---

**Need help?** Check the full [README.md](README.md) for detailed documentation.

