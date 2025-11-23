# ML Pipeline Infrastructure Setup Guide

This guide walks you through setting up the complete infrastructure for the Biomedical Data ML Pipeline.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11 or higher
- At least 8GB RAM available
- At least 50GB disk space

## Quick Start

### 1. Automated Setup (Recommended)

Run the automated setup script:

```bash
cd ml_pipeline
./setup_infrastructure.sh
```

This will:
- Start PostgreSQL, Redis, MinIO, MLflow, Prometheus, and Grafana
- Create necessary Docker volumes
- Verify service health

### 2. Manual Setup

If you prefer manual setup or need to customize:

#### Start Infrastructure Services

```bash
docker-compose -f docker-compose.infrastructure.yml up -d
```

#### Verify Services

```bash
# Check all services are running
docker-compose -f docker-compose.infrastructure.yml ps

# Check logs
docker-compose -f docker-compose.infrastructure.yml logs -f
```

## Service Configuration

### PostgreSQL Database

**Connection Details:**
- Host: localhost
- Port: 5432
- Database: ml_pipeline
- User: ml_user
- Password: ml_password

**Initialize Database Schema:**

```bash
python ml_pipeline/data_storage/init_db.py
```

**Verify Connection:**

```bash
docker exec -it ml_pipeline_postgres psql -U ml_user -d ml_pipeline
```

### Redis Cache

**Connection Details:**
- Host: localhost
- Port: 6379
- DB: 0

**Test Connection:**

```bash
docker exec -it ml_pipeline_redis redis-cli ping
# Should return: PONG
```

**Monitor Cache:**

```bash
docker exec -it ml_pipeline_redis redis-cli INFO stats
```

### MinIO Object Storage

**Access Details:**
- API Endpoint: http://localhost:9000
- Console: http://localhost:9001
- Access Key: minioadmin
- Secret Key: minioadmin

**Setup Bucket:**

1. Open MinIO Console: http://localhost:9001
2. Login with minioadmin/minioadmin
3. Create bucket: `alzheimer-ml-data`
4. Set bucket policy to private

**Test Upload:**

```python
from ml_pipeline.data_storage.object_storage import storage_client

# Upload test file
storage_client.upload_bytes(
    b"test data",
    "test/sample.txt"
)

# Verify
print(storage_client.object_exists("test/sample.txt"))
```

### MLflow Tracking Server

**Access:**
- URL: http://localhost:5000

**Features:**
- Experiment tracking
- Model registry
- Artifact storage

### Prometheus Monitoring

**Access:**
- URL: http://localhost:9090

**Metrics Available:**
- System metrics
- Application metrics
- Database metrics

### Grafana Dashboards

**Access:**
- URL: http://localhost:3000
- Username: admin
- Password: admin

**Setup:**
1. Add Prometheus as data source
2. Import ML Pipeline dashboards
3. Configure alerts

## Python Environment Setup

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r ml_pipeline/requirements.txt
```

### Configure Environment Variables

```bash
cp ml_pipeline/.env.example ml_pipeline/.env
# Edit .env with your configuration
```

## Verification

### Run Infrastructure Tests

```bash
cd ml_pipeline
pytest tests/test_infrastructure.py -v
```

Expected output:
```
test_infrastructure.py::TestDatabaseConnection::test_database_connection PASSED
test_infrastructure.py::TestDatabaseConnection::test_connection_pool PASSED
test_infrastructure.py::TestRedisCache::test_redis_connection PASSED
test_infrastructure.py::TestRedisCache::test_cache_set_get PASSED
test_infrastructure.py::TestObjectStorage::test_storage_connection PASSED
test_infrastructure.py::TestObjectStorage::test_upload_download PASSED
```

### Manual Verification

```python
# Test database
from ml_pipeline.data_storage.database import check_db_connection
print(f"Database: {check_db_connection()}")

# Test cache
from ml_pipeline.data_storage.cache import cache
print(f"Redis: {cache.health_check()}")

# Test storage
from ml_pipeline.data_storage.object_storage import storage_client
print(f"Storage: {storage_client.object_exists('test/sample.txt')}")
```

## Monitoring and Maintenance

### View Logs

```bash
# All services
docker-compose -f docker-compose.infrastructure.yml logs -f

# Specific service
docker-compose -f docker-compose.infrastructure.yml logs -f postgres
```

### Check Resource Usage

```bash
docker stats
```

### Backup Database

```bash
docker exec ml_pipeline_postgres pg_dump -U ml_user ml_pipeline > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker exec -i ml_pipeline_postgres psql -U ml_user -d ml_pipeline
```

### Clear Redis Cache

```bash
docker exec ml_pipeline_redis redis-cli FLUSHDB
```

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs ml_pipeline_postgres

# Restart service
docker-compose -f docker-compose.infrastructure.yml restart postgres
```

### Redis Connection Issues

```bash
# Check if Redis is running
docker ps | grep redis

# Test connection
docker exec ml_pipeline_redis redis-cli ping

# Restart service
docker-compose -f docker-compose.infrastructure.yml restart redis
```

### MinIO Connection Issues

```bash
# Check if MinIO is running
docker ps | grep minio

# Check health
curl http://localhost:9000/minio/health/live

# Restart service
docker-compose -f docker-compose.infrastructure.yml restart minio
```

### Port Conflicts

If ports are already in use, edit `docker-compose.infrastructure.yml` to use different ports:

```yaml
ports:
  - "5433:5432"  # PostgreSQL
  - "6380:6379"  # Redis
  - "9001:9000"  # MinIO
```

## Stopping Services

### Stop All Services

```bash
docker-compose -f docker-compose.infrastructure.yml down
```

### Stop and Remove Volumes (WARNING: Deletes all data)

```bash
docker-compose -f docker-compose.infrastructure.yml down -v
```

## Production Considerations

### Security

1. **Change Default Passwords:**
   - PostgreSQL: Update POSTGRES_PASSWORD
   - MinIO: Update MINIO_ROOT_USER and MINIO_ROOT_PASSWORD
   - Grafana: Change admin password

2. **Enable TLS:**
   - Configure SSL for PostgreSQL
   - Enable HTTPS for MinIO
   - Use TLS for Redis

3. **Network Security:**
   - Use Docker networks
   - Configure firewall rules
   - Implement access controls

### Performance

1. **Database Tuning:**
   - Adjust connection pool size
   - Configure shared_buffers
   - Optimize query performance

2. **Cache Optimization:**
   - Monitor hit rates
   - Adjust TTL values
   - Configure maxmemory policy

3. **Storage Optimization:**
   - Enable compression
   - Configure lifecycle policies
   - Monitor disk usage

### High Availability

1. **Database Replication:**
   - Set up PostgreSQL streaming replication
   - Configure automatic failover

2. **Redis Clustering:**
   - Deploy Redis Sentinel
   - Configure master-slave replication

3. **Object Storage:**
   - Use distributed MinIO setup
   - Configure erasure coding

## Next Steps

After infrastructure setup:

1. **Initialize Database Schema:**
   ```bash
   python ml_pipeline/data_storage/init_db.py
   ```

2. **Configure Data Sources:**
   - Set up ADNI API credentials
   - Configure OASIS data path
   - Configure NACC data path

3. **Start Data Ingestion:**
   - Implement data loaders
   - Run data validation
   - Extract features

4. **Train Models:**
   - Prepare training data
   - Configure hyperparameters
   - Start training pipeline

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review documentation
- Contact ML team
