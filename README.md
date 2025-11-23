# MemoryGuard

Alzheimer's Early Detection & Support Platform

## Overview

MemoryGuard is a comprehensive web application that combines advanced machine learning for early Alzheimer's detection with practical daily assistance features. Built for the AI for Alzheimer's hackathon, it provides:

- **Early Detection**: ML ensemble models analyzing biomedical data for risk assessment
- **Daily Assistance**: Memory aids, reminders, and routine tracking
- **Health Monitoring**: Comprehensive tracking of cognitive, biomarker, and lifestyle metrics
- **Community Support**: Connection with others and access to resources
- **Clinical Integration**: Healthcare provider portal and medical data analysis

## Technology Stack

### Frontend
- React 18 + TypeScript
- Three.js with React Three Fiber for 3D rendering
- Vite for build tooling
- Tailwind CSS for styling
- Zustand for state management

### Backend
- Python 3.11+ with FastAPI
- Supabase PostgreSQL for database
- Redis for caching
- SQLAlchemy ORM
- Celery for background tasks
- scikit-learn, XGBoost, TensorFlow for ML models

## Security & Compliance

MemoryGuard implements comprehensive security measures and HIPAA compliance:

- **Authentication**: Google OAuth 2.0 with JWT tokens
- **Rate Limiting**: Redis-backed rate limiting with per-endpoint quotas
- **Input Validation**: Centralized validation and sanitization middleware
- **Security Headers**: CSP, X-Frame-Options, HSTS, XSS Protection
- **Data Encryption**: Field-level encryption for PHI, TLS 1.3 in transit
- **Audit Logging**: Comprehensive audit trail for all PHI access
- **Access Controls**: Role-based access control (RBAC) with granular permissions
- **HIPAA Compliance**: Full HIPAA compliance documentation and procedures

📋 **Documentation**:
- [Security Policy](SECURITY_POLICY.md) - Security policies and procedures
- [HIPAA Compliance](backend/HIPAA_COMPLIANCE.md) - Detailed HIPAA compliance documentation
- [Imaging HIPAA Compliance](backend/IMAGING_HIPAA_COMPLIANCE.md) - Medical imaging security

🔒 **Reporting Security Issues**: Please email security@memoryguard.com (do not create public issues)

## Project Structure

```
memoryguard/
├── frontend/           # React + TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── store/
│   │   └── services/
│   └── package.json
├── backend/            # Python FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── ml/
│   │   └── services/
│   ├── alembic/
│   └── requirements.txt
└── docker-compose.yml
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)
- Supabase account (free tier available at https://supabase.com)

### Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd memoryguard
```

2. Set up Supabase (5 minutes):
   - See `SUPABASE_QUICKSTART.md` for step-by-step guide
   - Or use local PostgreSQL (default in docker-compose.yml)

3. Start all services:
```bash
# With local PostgreSQL (default)
docker-compose up -d

# Or with Supabase
docker-compose -f docker-compose.yml -f docker-compose.supabase.yml up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Supabase Dashboard: https://app.supabase.com

### Local Development Setup

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment Configuration

### Supabase Setup

1. Create a Supabase project at https://supabase.com
2. Get your database connection string from Settings → Database
3. Copy the example environment file:

```bash
cp backend/.env.example backend/.env
```

4. Update the `.env` file with your Supabase configuration:
   - `DATABASE_URL` - Your Supabase PostgreSQL connection string
   - `SUPABASE_URL` - Your Supabase project URL (optional)
   - `SUPABASE_KEY` - Your Supabase anon key (optional)
   - Redis URL
   - JWT secret
   - Google OAuth credentials
   - `DATA_ENCRYPTION_KEY` - Base64 Fernet key for encrypting sensitive fields
   - `AUDIT_LOG_PATH` - Absolute/relative path for JSONL audit logs

See `backend/SUPABASE_SETUP.md` for detailed setup instructions.

### Verify Supabase Connection

```bash
cd backend
python scripts/verify_supabase.py
```

## Database Migrations

Run database migrations:

```bash
cd backend
alembic upgrade head
```

Create a new migration:

```bash
alembic revision --autogenerate -m "Description"
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Workflow

1. Create a feature branch
2. Make your changes
3. Test locally
4. Submit a pull request

## Testing

### Frontend Tests
```bash
cd frontend
npm test
```

### Backend Tests
```bash
cd backend
pytest
```

## Deployment

See the deployment documentation in `docs/deployment.md` for production deployment instructions.

## Contributing

This project was created for the AI for Alzheimer's hackathon. Contributions are welcome!

## License

[License information to be added]

## Acknowledgments

Built for the AI for Alzheimer's hackathon to support early detection and daily assistance for individuals affected by Alzheimer's disease.
