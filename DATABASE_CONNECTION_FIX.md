# Database Connection Issues - Complete Fix

## Problems

1. **Reminders failing**: "Failed to create reminder: Request failed with status code 500"
2. **QR contacts not saving**: Contacts added but not appearing in QR code
3. **Root cause**: Database connection issues

## Diagnosis

Both issues indicate the PostgreSQL database isn't running or can't be reached.

## Solution

### Option 1: Start Local PostgreSQL (Recommended)

```bash
# Start PostgreSQL and Redis using Docker Compose
docker-compose up postgres redis -d

# Verify they're running
docker ps

# You should see:
# - postgres container on port 5432
# - redis container on port 6379
```

### Option 2: Use Supabase (Cloud Database)

If you don't have Docker or prefer cloud:

1. **Get your Supabase connection string**:
   - Go to https://supabase.com/dashboard
   - Select your project
   - Go to Settings → Database
   - Copy the "Connection string" (URI format)

2. **Update backend/.env**:
   ```bash
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres
   ```

3. **Restart backend**:
   ```bash
   # Stop backend (Ctrl+C)
   # Start again
   uvicorn app.main:app --reload --port 8000
   ```

## Quick Test

After starting the database, test if it's working:

```bash
# Test database connection
curl http://localhost:8000/health

# Should return: {"status": "healthy"}
```

## For QR Contacts Specifically

After fixing the database:

1. **Restart backend** to pick up the fix
2. **Go to Emergency page**
3. **Click "Edit"** on Medical Info
4. **Add a contact** using "+ Add Contact"
5. **Click "Save"** (IMPORTANT!)
6. **Generate QR code**
7. **Check backend logs** - you should see:
   ```
   INFO: Found X contacts in medical_info
   INFO: Using contacts from medical_info
   ```

## For Reminders Specifically

After fixing the database:

1. **Go to Memory Assistant page**
2. **Try adding a reminder**
3. **It should work now**

## Verify Database is Working

Run this in your terminal:

```bash
# If using local PostgreSQL
psql -h localhost -U memoryguard -d memoryguard -c "SELECT 1;"

# If using Supabase
# Just check if backend starts without errors
```

## Common Issues

### "Connection refused"
- Database isn't running
- Start with: `docker-compose up postgres redis -d`

### "Role does not exist"
- Wrong database credentials
- Check DATABASE_URL in backend/.env

### "Database does not exist"
- Need to create database
- Run migrations: `alembic upgrade head`

## Complete Reset (If Nothing Works)

```bash
# 1. Stop everything
docker-compose down

# 2. Remove old data
docker volume rm $(docker volume ls -q | grep memoryguard)

# 3. Start fresh
docker-compose up postgres redis -d

# 4. Wait 10 seconds for DB to initialize

# 5. Run migrations
cd backend
alembic upgrade head

# 6. Start backend
uvicorn app.main:app --reload --port 8000
```

## Check Backend Logs

When you try to add a reminder or save contacts, check the backend terminal for errors like:

```
sqlalchemy.exc.OperationalError: connection to server failed
```

This confirms it's a database connection issue.

## Next Steps

1. Start the database (Option 1 or 2 above)
2. Restart the backend
3. Try adding a reminder - should work
4. Try adding contacts and generating QR - should work

The fix I made to the QR code will work once the database is running and contacts are actually saved.
