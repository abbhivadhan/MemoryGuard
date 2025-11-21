# Supabase PostgreSQL Integration

## Overview

The application is now configured to use Supabase PostgreSQL as the database backend. This provides a managed PostgreSQL database with automatic backups, scaling, and a web-based management interface.

## What Changed

### 1. Database Configuration

The application already used PostgreSQL with SQLAlchemy, so minimal changes were needed:

- **Connection pooling** optimized for Supabase
- **SSL support** enabled by default
- **Connection timeout** and retry logic configured
- **Environment variables** for Supabase credentials

### 2. Documentation Added

- `SUPABASE_SETUP.md` - Comprehensive setup guide
- `SUPABASE_QUICKSTART.md` - 5-minute quick start
- `.env.example` - Example configuration with Supabase
- `docker-compose.supabase.yml` - Docker override for Supabase

### 3. Verification Tools

- `scripts/verify_supabase.py` - Connection verification script
- Checks connection, tables, migrations, and CRUD operations

## Architecture

```
┌─────────────────┐
│   Application   │
│   (FastAPI)     │
└────────┬────────┘
         │
         │ SQLAlchemy
         │ (PostgreSQL Driver)
         │
         ▼
┌─────────────────┐
│    Supabase     │
│   PostgreSQL    │
│   (Managed)     │
└─────────────────┘
```

## Features

### Current Implementation

✅ **Database Connection**
- SQLAlchemy ORM with Supabase PostgreSQL
- Connection pooling (5 connections, 10 overflow)
- Automatic connection health checks
- SSL encryption enabled

✅ **Migrations**
- Alembic for schema migrations
- All existing tables work with Supabase
- Version control for database schema

✅ **Models**
- User accounts and authentication
- Health metrics and assessments
- ML predictions and forecasts
- Medications and emergency contacts

✅ **Monitoring**
- Connection status logging
- Query performance tracking
- Error handling and retries

### Future Enhancements (Optional)

🔄 **Supabase Auth** (not implemented)
- Could replace Google OAuth with Supabase Auth
- Built-in user management
- Multiple auth providers

🔄 **Supabase Storage** (not implemented)
- Could store medical images
- File upload management
- CDN for fast delivery

🔄 **Supabase Realtime** (not implemented)
- Could add real-time features
- Live updates for health metrics
- Collaborative features

🔄 **Row Level Security** (not implemented)
- Could add RLS policies
- Database-level security
- Fine-grained access control

## Configuration

### Environment Variables

Required:
```bash
DATABASE_URL=postgresql://postgres:PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres
```

Optional (for future features):
```bash
SUPABASE_URL=https://PROJECT_REF.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
```

### Connection String Format

```
postgresql://[user]:[password]@[host]:[port]/[database]
```

Example:
```
postgresql://postgres:mypass123@db.abcdefg.supabase.co:5432/postgres
```

### Connection Pool Settings

```python
# In app/core/database.py
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,              # Base connections
    max_overflow=10,          # Additional connections
    pool_pre_ping=True,       # Health check before use
    pool_recycle=3600,        # Recycle after 1 hour
)
```

## Usage

### Local Development

1. **Set up Supabase**:
   ```bash
   # See SUPABASE_QUICKSTART.md
   ```

2. **Configure environment**:
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env with your Supabase credentials
   ```

3. **Run migrations**:
   ```bash
   cd backend
   alembic upgrade head
   ```

4. **Verify connection**:
   ```bash
   python scripts/verify_supabase.py
   ```

5. **Start application**:
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Development

1. **Using local PostgreSQL** (default):
   ```bash
   docker-compose up
   ```

2. **Using Supabase**:
   ```bash
   # Create .env with DATABASE_URL
   docker-compose -f docker-compose.yml -f docker-compose.supabase.yml up
   ```

### Production Deployment

1. **Set environment variables**:
   ```bash
   export DATABASE_URL="postgresql://postgres:PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres"
   export ENVIRONMENT=production
   ```

2. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

3. **Start services**:
   ```bash
   # Backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   
   # Celery worker
   celery -A celery_worker worker --loglevel=info
   ```

## Database Management

### Supabase Dashboard

Access your database through the Supabase dashboard:

1. **Table Editor**: View and edit data
2. **SQL Editor**: Run custom queries
3. **Database**: Monitor connections and performance
4. **Logs**: View database logs

### Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Add new table"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

### Backups

Supabase automatically backs up your database:
- **Free tier**: Daily backups, 7-day retention
- **Pro tier**: Point-in-time recovery

Manual backup:
```bash
pg_dump "postgresql://postgres:PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres" > backup.sql
```

Restore backup:
```bash
psql "postgresql://postgres:PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres" < backup.sql
```

## Monitoring

### Connection Health

Check connection status:
```python
from app.core.database import check_db_connection

if check_db_connection():
    print("Database connected")
```

### Query Performance

View slow queries in Supabase dashboard:
1. Go to **Database** → **Query Performance**
2. Identify slow queries
3. Add indexes to optimize

### Connection Pool

Monitor connection pool:
```python
from app.core.database import engine

print(f"Pool size: {engine.pool.size()}")
print(f"Checked out: {engine.pool.checkedout()}")
```

## Security

### Best Practices

1. **Never commit credentials**:
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Use service role key carefully**:
   - Only use server-side
   - Never expose to frontend

3. **Enable SSL**:
   - Supabase enforces SSL by default
   - Connection string uses SSL automatically

4. **Rotate passwords**:
   - Change database password periodically
   - Update in Supabase dashboard

5. **Monitor access**:
   - Check connection logs
   - Review query patterns

### Connection Security

All connections use:
- SSL/TLS encryption
- Password authentication
- Connection pooling with health checks
- Automatic retry on failure

## Troubleshooting

### Common Issues

1. **Connection timeout**:
   - Check internet connection
   - Verify Supabase project is active
   - Increase timeout in connection args

2. **Too many connections**:
   - Reduce pool_size
   - Check for connection leaks
   - Upgrade Supabase plan

3. **Authentication failed**:
   - Verify password is correct
   - Check for special characters
   - Reset password in dashboard

4. **SSL required**:
   - Add `?sslmode=require` to connection string
   - Supabase enforces SSL by default

### Debug Mode

Enable SQL query logging:
```python
# In app/core/config.py
DEBUG = True  # Logs all SQL queries
```

### Support

- **Supabase Discord**: https://discord.supabase.com
- **Supabase Docs**: https://supabase.com/docs
- **GitHub Issues**: [Your repo]

## Performance

### Optimization Tips

1. **Add indexes**:
   ```sql
   CREATE INDEX idx_users_email ON users(email);
   ```

2. **Use connection pooling**:
   - Already configured
   - Adjust pool_size if needed

3. **Optimize queries**:
   - Use EXPLAIN ANALYZE
   - Add appropriate indexes
   - Avoid N+1 queries

4. **Cache frequently accessed data**:
   - Use Redis for caching
   - Reduce database load

### Benchmarks

Expected performance:
- Simple query: 10-50ms
- Complex query: 50-200ms
- Connection establishment: 50-100ms

## Cost

### Free Tier

- 500 MB database
- 2 GB bandwidth
- 60 concurrent connections
- 7-day backup retention

### When to Upgrade

Consider upgrading when:
- Database size > 500 MB
- Need more connections
- Require point-in-time recovery
- Need dedicated resources

## Migration from Local PostgreSQL

If you have existing data in local PostgreSQL:

1. **Backup local database**:
   ```bash
   pg_dump -U postgres memoryguard > backup.sql
   ```

2. **Restore to Supabase**:
   ```bash
   psql "postgresql://postgres:PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres" < backup.sql
   ```

3. **Verify data**:
   ```bash
   python scripts/verify_supabase.py
   ```

## Summary

The application now uses Supabase PostgreSQL with:
- ✅ Optimized connection pooling
- ✅ SSL encryption
- ✅ Automatic backups
- ✅ Web-based management
- ✅ Scalable infrastructure
- ✅ Minimal code changes

All existing features work seamlessly with Supabase!
