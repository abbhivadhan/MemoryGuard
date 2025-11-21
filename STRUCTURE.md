# MemoryGuard Project Structure

This document describes the organization of the MemoryGuard codebase.

## Root Directory

```
memoryguard/
├── frontend/              # React + TypeScript frontend application
├── backend/               # Python FastAPI backend application
├── .kiro/                 # Kiro AI assistant specifications
├── docker-compose.yml     # Docker Compose configuration
├── Makefile              # Development commands
├── README.md             # Project overview
├── SETUP.md              # Setup instructions
├── STRUCTURE.md          # This file
├── setup.sh              # Automated setup script
├── .gitignore            # Git ignore rules
└── .dockerignore         # Docker ignore rules
```

## Frontend Structure

```
frontend/
├── src/
│   ├── components/       # React components (to be organized)
│   │   ├── 3d/          # Three.js 3D components
│   │   ├── auth/        # Authentication components
│   │   ├── dashboard/   # Dashboard components
│   │   ├── memory/      # Memory assistant components
│   │   └── cognitive/   # Cognitive assessment components
│   ├── pages/           # Page components
│   ├── hooks/           # Custom React hooks
│   ├── store/           # Zustand state management
│   ├── services/        # API services
│   ├── App.tsx          # Main App component
│   ├── main.tsx         # Application entry point
│   ├── index.css        # Global styles
│   └── vite-env.d.ts    # Vite type definitions
├── public/              # Static assets
├── index.html           # HTML template
├── package.json         # NPM dependencies
├── tsconfig.json        # TypeScript configuration
├── vite.config.ts       # Vite configuration
├── tailwind.config.js   # Tailwind CSS configuration
├── postcss.config.js    # PostCSS configuration
├── .eslintrc.cjs        # ESLint configuration
├── Dockerfile           # Docker configuration
├── .dockerignore        # Docker ignore rules
└── .gitignore           # Git ignore rules
```

### Frontend Key Files

- **src/main.tsx**: Application entry point, renders the root component
- **src/App.tsx**: Main application component with routing
- **vite.config.ts**: Vite build configuration with proxy setup
- **tailwind.config.js**: Tailwind CSS customization
- **package.json**: Dependencies including React, Three.js, Zustand, React Query

## Backend Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/          # API version 1 endpoints
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── ml.py           # ML prediction endpoints
│   │       ├── health.py       # Health metrics endpoints
│   │       ├── assessments.py  # Cognitive assessment endpoints
│   │       ├── medications.py  # Medication tracking endpoints
│   │       ├── imaging.py      # Medical imaging endpoints
│   │       └── community.py    # Community forum endpoints
│   ├── core/
│   │   ├── config.py    # Application configuration
│   │   ├── security.py  # Security utilities (JWT, encryption)
│   │   └── database.py  # Database connection
│   ├── models/          # SQLAlchemy database models
│   │   ├── user.py
│   │   ├── health_metric.py
│   │   ├── assessment.py
│   │   ├── medication.py
│   │   └── prediction.py
│   ├── ml/              # Machine learning modules
│   │   ├── models/
│   │   │   ├── ensemble.py
│   │   │   ├── random_forest.py
│   │   │   ├── xgboost_model.py
│   │   │   └── neural_net.py
│   │   ├── preprocessing.py
│   │   ├── interpretability.py
│   │   └── imaging_analysis.py
│   ├── services/        # Business logic services
│   │   ├── auth_service.py
│   │   ├── ml_service.py
│   │   ├── notification_service.py
│   │   └── imaging_service.py
│   ├── tasks/           # Celery background tasks
│   │   ├── ml_training.py
│   │   └── data_sync.py
│   └── main.py          # FastAPI application entry point
├── alembic/             # Database migrations
│   ├── versions/        # Migration files
│   ├── env.py          # Alembic environment
│   └── script.py.mako  # Migration template
├── tests/               # Backend tests
├── requirements.txt     # Python dependencies
├── alembic.ini         # Alembic configuration
├── .env.example        # Example environment variables
├── Dockerfile          # Docker configuration
├── .dockerignore       # Docker ignore rules
└── .gitignore          # Git ignore rules
```

### Backend Key Files

- **app/main.py**: FastAPI application with CORS and middleware setup
- **app/core/config.py**: Environment-based configuration using Pydantic
- **requirements.txt**: Python dependencies including FastAPI, ML libraries
- **alembic.ini**: Database migration configuration

## Docker Configuration

### docker-compose.yml

Defines 5 services:

1. **postgres**: PostgreSQL 15 database
   - Port: 5432
   - Volume: postgres_data

2. **redis**: Redis 7 cache
   - Port: 6379
   - Volume: redis_data

3. **backend**: FastAPI application
   - Port: 8000
   - Depends on: postgres, redis

4. **frontend**: React application
   - Port: 3000
   - Depends on: backend

5. **celery-worker**: Background task processor
   - Depends on: postgres, redis

### Dockerfiles

- **frontend/Dockerfile**: Node.js 20 Alpine image
- **backend/Dockerfile**: Python 3.11 Slim image

## Configuration Files

### Environment Variables

- **backend/.env**: Backend configuration (database, Redis, JWT, OAuth)
- **backend/.env.example**: Template for environment variables

### Build Configuration

- **frontend/vite.config.ts**: Vite build and dev server configuration
- **frontend/tsconfig.json**: TypeScript compiler options
- **frontend/tailwind.config.js**: Tailwind CSS customization

### Linting and Formatting

- **frontend/.eslintrc.cjs**: ESLint rules for TypeScript/React

## Development Tools

### Makefile Commands

```bash
make help              # Show available commands
make build             # Build Docker containers
make up                # Start all services
make down              # Stop all services
make logs              # View logs
make clean             # Remove containers and volumes
make install-frontend  # Install frontend dependencies
make install-backend   # Install backend dependencies
make test              # Run all tests
```

### Setup Script

- **setup.sh**: Automated setup script that:
  - Checks for Docker and Docker Compose
  - Creates .env file from example
  - Builds Docker images
  - Starts all services
  - Displays service status

## Data Flow

```
User Browser
    ↓
Frontend (React + Three.js)
    ↓ HTTP/WebSocket
Backend API (FastAPI)
    ↓
┌───────────┬──────────┬──────────┐
│           │          │          │
PostgreSQL  Redis    ML Models   Celery
(Data)    (Cache)  (Predictions) (Tasks)
```

## API Structure

All API endpoints are versioned under `/api/v1/`:

- `/api/v1/auth/*` - Authentication
- `/api/v1/ml/*` - Machine learning predictions
- `/api/v1/health/*` - Health metrics
- `/api/v1/assessments/*` - Cognitive assessments
- `/api/v1/medications/*` - Medication tracking
- `/api/v1/imaging/*` - Medical imaging
- `/api/v1/community/*` - Community features

## Testing Structure

### Frontend Tests
- Unit tests: Jest + React Testing Library
- E2E tests: Playwright (to be added)

### Backend Tests
- Unit tests: pytest
- Integration tests: pytest with test database

## Future Directories (To Be Created)

As development progresses, these directories will be added:

### Frontend
- `src/components/3d/` - Three.js components
- `src/components/auth/` - Authentication UI
- `src/components/dashboard/` - Dashboard components
- `src/hooks/` - Custom React hooks
- `src/store/` - Zustand stores
- `src/services/` - API client services

### Backend
- `app/api/v1/` - API endpoint implementations
- `app/models/` - Database models
- `app/ml/models/` - ML model implementations
- `app/services/` - Business logic
- `tests/` - Test files

## Notes

- All Python code follows PEP 8 style guidelines
- All TypeScript code follows ESLint configuration
- Database migrations are managed with Alembic
- API documentation is auto-generated by FastAPI
- 3D rendering uses Three.js with React Three Fiber
- State management uses Zustand for simplicity
- ML models use ensemble approach (Random Forest, XGBoost, Neural Networks)
