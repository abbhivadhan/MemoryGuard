# Supabase PostgreSQL Setup

This guide explains how to configure the application to use Supabase PostgreSQL as the database.

## Overview

The application uses Supabase's PostgreSQL database for storing:
- User accounts and profiles
- Health metrics and assessments
- ML predictions and forecasts
- Medications and emergency contacts

## Prerequisites

1. Supabase account (free tier available at https://supabase.com)
2. A Supabase project created

## Step 1: Create Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Fill in project details:
   - **Name**: memoryguard (or your preferred name)
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose closest to your users
4. Wait for project to be provisioned (~2 minutes)

## Step 2: Get Database Connection String

1. In your Supabase project dashboard, go to **Settings** → **Database**
2. Scroll down to **Connection string** section
3. Select **URI** tab
4. Copy the connection string (it looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your actual database password

### Connection String Format

```
postgresql://postgres:YOUR_PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres
```

**Components:**
- `postgres` - default username
- `YOUR_PASSWORD` - database password you set
- `db.PROJECT_REF.supabase.co` - your Supabase database host
- `5432` - PostgreSQL port
- `postgres` - database name

## Step 3: Configure Environment Variables

### Backend Configuration

Update your `backend/.env` file:

```bash
# Supabase Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres

# Optional: Supabase API (for future use)
SUPABASE_URL=https://PROJECT_REF.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here
```

**To get API keys:**
1. Go to **Settings** → **API**
2. Copy `anon` `public` key for SUPABASE_KEY
3. Copy `service_role` key for SUPABASE_SERVICE_KEY (keep this secret!)

### Docker Configuration

Update `docker-compose.yml` to use Supabase instead of local PostgreSQL:

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres
    # Remove or comment out the postgres service dependency
    # depends_on:
    #   - postgres
  
  # Comment out or remove local postgres service
  # postgres:
  #   image: postgres:15
  #   ...
```

## Step 4: Run Database Migrations

The application uses Alembic for database migrations. Run migrations to create tables:

```bash
cd backend

# Run migrations
alembic upgrade head
```

This will create all necessary tables in your Supabase database:
- users
- health_metrics
- assessments
- medications
- emergency_contacts
- predictions
- and more...

## Step 5: Verify Connection

Test the database connection:

```bash
cd backend
python -c "from app.core.database import check_db_connection; print('Connected!' if check_db_connection() else 'Failed')"
```

Or start the backend and check logs:

```bash
uvicorn app.main:app --reload
```

Look for: `"Supabase database connection established"`

## Supabase Dashboard Features

### Table Editor

View and edit data directly:
1. Go to **Table Editor** in Supabase dashboard
2. Browse tables created by migrations
3. Add, edit, or delete records

### SQL Editor

Run custom SQL queries:
1. Go to **SQL Editor**
2. Write and execute SQL queries
3. Save frequently used queries

### Database Backups

Supabase automatically backs up your database:
- **Free tier**: Daily backups, 7-day retention
- **Pro tier**: Point-in-time recovery

To restore:
1. Go to **Settings** → **Database**
2. Scroll to **Backups** section
3. Select backup and restore

## Connection Pooling

The application is configured for optimal Supabase connection pooling:

```python
# In app/core/database.py
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,              # 5 connections in pool
    max_overflow=10,          # Up to 15 total connections
    pool_pre_ping=True,       # Verify connections before use
    pool_recycle=3600,        # Recycle after 1 hour
)
```

**Supabase Connection Limits:**
- **Free tier**: 60 connections
- **Pro tier**: 200 connections
- **Enterprise**: Custom limits

## Security Best Practices

### 1. Use Environment Variables

Never commit credentials to git:

```bash
# .gitignore should include:
.env
.env.local
.env.production
```

### 2. Use Service Role Key Carefully

The service role key bypasses Row Level Security (RLS). Only use it server-side.

### 3. Enable SSL

Supabase enforces SSL by default. The connection string uses SSL automatically.

### 4. Row Level Security (Optional)

Enable RLS for additional security:

```sql
-- In Supabase SQL Editor
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policy (example)
CREATE POLICY "Users can view own data"
ON users FOR SELECT
USING (auth.uid() = id);
```

## Monitoring

### Connection Stats

Check active connections in Supabase dashboard:
1. Go to **Settings** → **Database**
2. View **Connection pooling** section
3. Monitor active connections

### Query Performance

Use Supabase's query analyzer:
1. Go to **Database** → **Query Performance**
2. View slow queries
3. Optimize with indexes

### Logs

View database logs:
1. Go to **Logs** → **Postgres Logs**
2. Filter by severity
3. Debug connection issues

## Troubleshooting

### Connection Timeout

**Error**: `connection timeout`

**Solutions:**
1. Check your internet connection
2. Verify DATABASE_URL is correct
3. Check Supabase project is not paused (free tier pauses after inactivity)
4. Increase `connect_timeout` in connection args

### Too Many Connections

**Error**: `too many connections`

**Solutions:**
1. Reduce `pool_size` in database.py
2. Ensure connections are properly closed
3. Upgrade Supabase plan for more connections
4. Use connection pooling (PgBouncer)

### SSL Required

**Error**: `SSL required`

**Solution:**
Add SSL mode to connection string:
```
postgresql://postgres:PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres?sslmode=require
```

### Authentication Failed

**Error**: `authentication failed`

**Solutions:**
1. Verify password is correct
2. Check for special characters (URL encode if needed)
3. Reset database password in Supabase dashboard

## Migration from Local PostgreSQL

If migrating from local PostgreSQL:

### 1. Backup Local Data

```bash
pg_dump -U postgres memoryguard > backup.sql
```

### 2. Restore to Supabase

```bash
psql "postgresql://postgres:PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres" < backup.sql
```

### 3. Verify Data

Check tables in Supabase Table Editor

## Performance Optimization

### Indexes

Create indexes for frequently queried columns:

```sql
-- In Supabase SQL Editor
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_health_metrics_user_id ON health_metrics(user_id);
CREATE INDEX idx_predictions_user_id ON predictions(user_id);
```

### Query Optimization

Use EXPLAIN ANALYZE to optimize queries:

```sql
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'user@example.com';
```

## Cost Considerations

### Free Tier Limits
- 500 MB database space
- 2 GB bandwidth
- 60 concurrent connections
- 7-day backup retention

### When to Upgrade
- Database size > 500 MB
- Need more connections
- Require point-in-time recovery
- Need dedicated resources

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

## Support

- Supabase Discord: https://discord.supabase.com
- Supabase GitHub: https://github.com/supabase/supabase
- Project Issues: [Your GitHub repo]
