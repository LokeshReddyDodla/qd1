# Docker Deployment Guide

This guide explains how to deploy the Patient Health Data RAG System using Docker and Docker Compose.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- OpenAI API Key

## 🏗️ Architecture

The Docker setup includes 4 services:

1. **Qdrant** - Vector database for embeddings (port 6333)
2. **PostgreSQL** - Relational database for patient metadata (port 5432)
3. **MongoDB** - Document database for source data (port 27017)
4. **FastAPI App** - Python application (port 1531)

All services communicate via a Docker network and use persistent volumes for data.

## 🚀 Quick Start

### 1. Configure Environment Variables

Copy the environment template:
```bash
cp .env.docker .env
```

Edit `.env` and add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 2. Build and Start All Services

```bash
# Build and start all containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

### 3. Verify Deployment

Check if all services are healthy:
```bash
# Check Qdrant
curl http://localhost:6333/health

# Check FastAPI application
curl http://localhost:1531/health

# Check collections
curl http://localhost:1531/
```

### 4. Access the Application

- **Frontend UI**: http://localhost:1531
- **API Documentation**: http://localhost:1531/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Health Check**: http://localhost:1531/health

## 📦 Docker Commands Reference

### Starting Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d app

# Start with logs visible
docker-compose up
```

### Stopping Services

```bash
# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove containers + volumes (DELETES ALL DATA)
docker-compose down -v
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f qdrant

# Last 100 lines
docker-compose logs --tail=100 app
```

### Rebuilding After Code Changes

```bash
# Rebuild app container
docker-compose build app

# Rebuild and restart
docker-compose up -d --build app

# Force complete rebuild
docker-compose build --no-cache app
```

### Executing Commands Inside Containers

```bash
# Shell into app container
docker-compose exec app bash

# Run Python script
docker-compose exec app python check_patient_data.py <patient_id>

# Check Python version
docker-compose exec app python --version
```

## 🔧 Configuration

### Environment Variables

All configuration is done via environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `QDRANT_HOST` | Qdrant hostname | `qdrant` |
| `QDRANT_PORT` | Qdrant port | `6333` |
| `QDRANT_COLLECTION_NAME` | Collection name | `people_data` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | Environment name | `production` |

### Port Mapping

To change exposed ports, edit `docker-compose.yml`:

```yaml
services:
  app:
    ports:
      - "8080:1531"  # Change 8080 to your desired port
```

### Resource Limits

Add resource limits to prevent memory issues:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 💾 Data Persistence

All data is stored in Docker volumes:

| Volume | Purpose | Location |
|--------|---------|----------|
| `qdrant_storage` | Vector embeddings | `/qdrant/storage` |
| `postgres_data` | Patient metadata | `/var/lib/postgresql/data` |
| `mongo_data` | Source documents | `/data/db` |

### Backup Data

```bash
# Backup Qdrant data
docker run --rm -v qd2_qdrant_storage:/source -v $(pwd)/backups:/backup \
  alpine tar czf /backup/qdrant-$(date +%Y%m%d).tar.gz -C /source .

# Backup PostgreSQL
docker-compose exec postgres pg_dump -U postgres patient_db > backups/postgres-$(date +%Y%m%d).sql

# Backup MongoDB
docker-compose exec mongodb mongodump --out=/backup/mongo-$(date +%Y%m%d)
```

### Restore Data

```bash
# Restore Qdrant
docker run --rm -v qd2_qdrant_storage:/target -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/qdrant-20231025.tar.gz -C /target

# Restore PostgreSQL
cat backups/postgres-20231025.sql | docker-compose exec -T postgres psql -U postgres patient_db

# Restore MongoDB
docker-compose exec mongodb mongorestore /backup/mongo-20231025
```

## 🐛 Troubleshooting

### Service Won't Start

Check logs for errors:
```bash
docker-compose logs app
```

### Cannot Connect to Qdrant

Ensure Qdrant is healthy:
```bash
docker-compose ps qdrant
curl http://localhost:6333/health
```

### OpenAI API Errors

Verify API key is set:
```bash
docker-compose exec app env | grep OPENAI_API_KEY
```

### Out of Memory

Increase Docker memory limit in Docker Desktop settings or add limits to docker-compose.yml.

### Reset Everything

**⚠️ WARNING: This deletes all data!**
```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

## 📊 Monitoring

### Check Service Health

```bash
# All services
docker-compose ps

# Specific service health
docker inspect --format='{{json .State.Health}}' qd2-app | jq

# Resource usage
docker stats
```

### View Qdrant Collections

```bash
# List collections
curl http://localhost:6333/collections

# Collection info
curl http://localhost:6333/collections/people_data
```

## 🚢 Production Deployment

### Use Docker Secrets for API Keys

```yaml
# docker-compose.prod.yml
services:
  app:
    secrets:
      - openai_api_key
    environment:
      - OPENAI_API_KEY=/run/secrets/openai_api_key

secrets:
  openai_api_key:
    file: ./secrets/openai_api_key.txt
```

### Use Reverse Proxy (Nginx)

```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:1531;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Enable HTTPS with Let's Encrypt

```yaml
# Add to docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
```

## 📈 Scaling

### Multiple App Instances

```bash
# Scale to 3 instances
docker-compose up -d --scale app=3
```

### External Qdrant Cluster

Edit `docker-compose.yml` to point to external Qdrant:

```yaml
services:
  app:
    environment:
      - QDRANT_HOST=your-qdrant-cluster.com
      - QDRANT_PORT=6333
```

## 🔒 Security Checklist

- ✅ Use `.env` file for secrets (never commit to git)
- ✅ Change default PostgreSQL password
- ✅ Enable authentication on MongoDB
- ✅ Use HTTPS in production
- ✅ Restrict network access with firewall rules
- ✅ Regular security updates: `docker-compose pull`
- ✅ Use Docker secrets for sensitive data
- ✅ Run containers as non-root user (already configured)

## 📚 Additional Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)

## 🆘 Support

For issues and questions:
1. Check logs: `docker-compose logs -f`
2. Verify health: `docker-compose ps`
3. Review configuration in `.env`
4. Check port conflicts: `lsof -i :1531`
