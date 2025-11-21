# Database Migrations Guide

This document explains how to manage database migrations for the MemoryGuard application.

## Overview

We use Alembic for database migrations. All migration files are located in `backend/alembic/versions/`.

## Current Migrations

### Migration 001: Create Users Table
- Creates the `users` table with authentication and profile fields
- Adds APOE genotype support
- Creates indexes for email and google_id

### Migration 002: Create Health Data Tables
- Creates `health_metrics` table for tracking cognitive, biomarker, imaging, lifestyle, and cardiovascular metrics
- Creates `assessments` table for cognitive test results (MMSE, MoCA, CDR, Clock Drawing)
- Creates `medications` table for medication tracking and adherence
- Creates `predictions` table for ML risk assessment results with SHAP values
- Creates `emergency_contacts` table for emergency contact information
- Creates `caregiver_relationships` table for caregiver access management
- Creates `provider_relationships` table for healthcare provider access
- Adds comprehensive indexes for query optimization

## Running Migrations

### Using Docker (Recommended)

1. **Start the services:**
   ```bash
   make up
   ```

2. **Run migrations:**
   ```bash
   make migrate
   ```

   Or directly:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

### Using Local Environment

1. **Ensure PostgreSQL is running and accessible**

2. **Set environment variables:**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/memoryguard"
   ```

3. **Run migrations:**
   ```bash
   cd backend
   alembic upgrade head
   ```

   Or use the script:
   ```bash
   ./backend/run_migrations.sh
   ```

## Creating New Migrations

### Auto-generate from model changes:
```bash
cd backend
alembic revision --autogenerate -m "description of changes"
```

### Create empty migration:
```bash
cd backend
alembic revision -m "description of changes"
```

### Review and edit the generated migration file in `backend/alembic/versions/`

## Migration Commands

- **Upgrade to latest:** `alembic upgrade head`
- **Upgrade one version:** `alembic upgrade +1`
- **Downgrade one version:** `alembic downgrade -1`
- **Show current version:** `alembic current`
- **Show migration history:** `alembic history`
- **Downgrade to specific version:** `alembic downgrade <revision>`

## Troubleshooting

### Migration fails with "relation already exists"
This usually means the database already has some tables. You can:
1. Drop all tables and re-run migrations (development only)
2. Mark migrations as applied: `alembic stamp head`

### Check current database state:
```bash
docker-compose exec backend alembic current
```

### View migration history:
```bash
docker-compose exec backend alembic history --verbose
```

## Database Schema

### Tables Created by Migration 002:

1. **health_metrics** - Health indicator tracking
   - Supports: cognitive, biomarker, imaging, lifestyle, cardiovascular metrics
   - Indexed by: user_id, type, name, timestamp
   - Requirements: 11.1-11.6

2. **assessments** - Cognitive test results
   - Supports: MMSE, MoCA, CDR, Clock Drawing tests
   - Stores responses as JSON
   - Indexed by: user_id, type, completed_at
   - Requirements: 12.1, 12.4

3. **medications** - Medication tracking
   - Tracks schedule and adherence
   - Stores side effects
   - Indexed by: user_id, active, start_date
   - Requirements: 13.1, 13.3, 13.4

4. **predictions** - ML prediction results
   - Stores risk scores and confidence intervals
   - Includes SHAP feature importance
   - Stores progression forecasts (6, 12, 24 months)
   - Indexed by: user_id, prediction_date, risk_category
   - Requirements: 3.3, 3.4, 4.1

5. **emergency_contacts** - Emergency contact information
   - Stores contact details and relationships
   - Priority-based ordering
   - Indexed by: user_id, active, priority
   - Requirements: 14.3

6. **caregiver_relationships** - Caregiver access management
   - Manages permissions for caregivers
   - Tracks approval status
   - Indexed by: patient_id, caregiver_id, active
   - Requirements: 6.1

7. **provider_relationships** - Healthcare provider access
   - Manages provider permissions
   - Tracks approval status
   - Indexed by: patient_id, provider_id, active
   - Requirements: 6.1

## Notes

- All tables use UUID primary keys
- All tables include `created_at` and `updated_at` timestamps
- Foreign keys use CASCADE delete to maintain referential integrity
- Comprehensive indexes are created for common query patterns
- JSON columns are used for flexible data storage (responses, feature_importance, etc.)
- ARRAY columns are used for lists (schedule, side_effects, recommendations)
