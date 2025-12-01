# 🏗️ Deployment Architecture

## Current Setup

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│                    (Vercel - Deployed ✅)                    │
│                                                              │
│  • React + TypeScript + Vite                                │
│  • 3D Visualizations (Three.js)                             │
│  • PWA with offline support                                 │
│  • URL: https://your-app.vercel.app                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTPS API Calls
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                         BACKEND                              │
│                    (Render - To Deploy 🚀)                   │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           FastAPI Application                       │    │
│  │  • Python 3.11                                      │    │
│  │  • Gunicorn + Uvicorn workers                       │    │
│  │  • JWT Authentication                               │    │
│  │  • ML Models (scikit-learn, XGBoost, TensorFlow)   │    │
│  │  • Medical imaging processing                       │    │
│  │  • URL: https://your-backend.onrender.com          │    │
│  └────────────┬───────────────────┬────────────────────┘    │
│               │                   │                          │
│               │                   │                          │
│  ┌────────────▼──────────┐   ┌───▼──────────────────┐      │
│  │   PostgreSQL DB       │   │   Redis Cache         │      │
│  │  (Render Managed)     │   │  (Render Managed)     │      │
│  │                       │   │                       │      │
│  │  • User data          │   │  • Session cache      │      │
│  │  • Health metrics     │   │  • Rate limiting      │      │
│  │  • Assessments        │   │  • Celery queue       │      │
│  │  • ML predictions     │   │                       │      │
│  │  • 1GB free tier      │   │  • 25MB free tier     │      │
│  └───────────────────────┘   └───────────────────────┘      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Celery Worker (Optional)                    │    │
│  │  • Background ML processing                         │    │
│  │  • Async tasks                                      │    │
│  │  • Email notifications                              │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
                       │
                       │ API Calls
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   EXTERNAL SERVICES                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Google     │  │   Google     │  │   Sentry     │     │
│  │   OAuth      │  │   Gemini AI  │  │   (Optional) │     │
│  │              │  │              │  │              │     │
│  │ • Login      │  │ • Chat       │  │ • Error      │     │
│  │ • Auth       │  │ • Health     │  │   tracking   │     │
│  │              │  │   advice     │  │ • Monitoring │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

## Deployment Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT PROCESS                        │
└─────────────────────────────────────────────────────────────┘

1. PREPARE
   ├── Generate secrets (JWT, encryption keys)
   ├── Gather API keys (Google OAuth, Gemini)
   └── Get Vercel frontend URL

2. CREATE INFRASTRUCTURE
   ├── PostgreSQL Database
   │   └── Copy Internal Database URL
   ├── Redis Cache
   │   └── Copy Internal Redis URL
   └── Web Service
       └── Configure build & start commands

3. CONFIGURE ENVIRONMENT
   ├── Add DATABASE_URL
   ├── Add REDIS_URL
   ├── Add JWT_SECRET
   ├── Add Google OAuth credentials
   ├── Add Gemini API key
   └── Add CORS_ORIGINS with Vercel URL

4. DEPLOY
   ├── Render builds Docker image
   ├── Installs dependencies (pip install)
   ├── Runs migrations (alembic upgrade head)
   ├── Starts Gunicorn server
   └── Health check passes

5. VERIFY
   ├── Test root endpoint (/)
   ├── Test API docs (/docs)
   ├── Test health check (/api/v1/health)
   └── Test from frontend

6. CONNECT FRONTEND
   ├── Update VITE_API_URL in Vercel
   ├── Redeploy frontend
   └── Test end-to-end flow
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERACTION                        │
└─────────────────────────────────────────────────────────────┘

USER → FRONTEND (Vercel)
  │
  ├─→ Login with Google
  │   └─→ BACKEND → Google OAuth → JWT Token → Redis Cache
  │
  ├─→ View Dashboard
  │   └─→ BACKEND → PostgreSQL → Health Metrics → FRONTEND
  │
  ├─→ Take Assessment
  │   └─→ BACKEND → PostgreSQL → Save Results → ML Prediction
  │       └─→ Celery Worker → ML Models → Risk Score → FRONTEND
  │
  ├─→ Chat with AI
  │   └─→ BACKEND → Google Gemini API → Response → FRONTEND
  │
  └─→ Upload Brain Scan
      └─→ BACKEND → Process Image → PostgreSQL → FRONTEND
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                         │
└─────────────────────────────────────────────────────────────┘

1. TRANSPORT LAYER
   ├── HTTPS/TLS (automatic on Render & Vercel)
   ├── Secure headers (CSP, HSTS, X-Frame-Options)
   └── CORS restrictions

2. AUTHENTICATION
   ├── Google OAuth 2.0
   ├── JWT tokens (15 min access, 7 day refresh)
   └── Redis session management

3. AUTHORIZATION
   ├── Role-based access control (RBAC)
   ├── PHI access logging
   └── Audit trail

4. DATA PROTECTION
   ├── Encrypted database connections
   ├── Encrypted medical imaging storage
   ├── Input validation & sanitization
   └── Rate limiting

5. MONITORING
   ├── Sentry error tracking
   ├── Audit logs
   ├── Performance metrics
   └── Security alerts
```

## Scaling Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    SCALING OPTIONS                           │
└─────────────────────────────────────────────────────────────┘

FREE TIER (Current)
├── Web Service: 1 instance (sleeps after 15 min)
├── Database: 1GB storage
├── Redis: 25MB storage
└── Cost: $0/month

STARTER ($24/month)
├── Web Service: 1 instance (always on)
├── Database: 256MB RAM, 1GB storage, backups
├── Redis: 100MB storage
└── Good for: 100-1000 users

PROFESSIONAL ($100+/month)
├── Web Service: 2-4 instances (load balanced)
├── Database: 1GB RAM, 10GB storage, backups
├── Redis: 1GB storage
└── Good for: 1000-10000 users

ENTERPRISE (Custom)
├── Web Service: Auto-scaling
├── Database: High availability, replicas
├── Redis: Cluster mode
└── Good for: 10000+ users
```

## Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────┐
│                      MONITORING STACK                        │
└─────────────────────────────────────────────────────────────┘

RENDER DASHBOARD
├── Real-time logs
├── CPU & Memory metrics
├── Request rate & latency
└── Error rate

SENTRY (Optional)
├── Error tracking
├── Performance monitoring
├── User session replay
└── Release tracking

APPLICATION LOGS
├── Structured JSON logging
├── Request/response logging
├── Audit trail
└── ML model performance

HEALTH CHECKS
├── /api/v1/health endpoint
├── Database connectivity
├── Redis connectivity
└── External API status
```

## Backup & Recovery

```
┌─────────────────────────────────────────────────────────────┐
│                   BACKUP STRATEGY                            │
└─────────────────────────────────────────────────────────────┘

DATABASE BACKUPS (Paid Plans)
├── Automatic daily backups
├── Point-in-time recovery
├── 7-day retention
└── Manual backup on demand

APPLICATION STATE
├── ML models versioned in registry
├── Configuration in environment variables
├── Code in GitHub
└── Infrastructure as code (render.yaml)

DISASTER RECOVERY
├── Database restore from backup
├── Redeploy from GitHub
├── Restore environment variables
└── RTO: < 1 hour, RPO: < 24 hours
```

## Development Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                  DEVELOPMENT PIPELINE                        │
└─────────────────────────────────────────────────────────────┘

LOCAL DEVELOPMENT
├── Docker Compose (PostgreSQL + Redis)
├── Hot reload with uvicorn
├── Local testing
└── Git commit

STAGING (Optional)
├── Separate Render service
├── Staging database
├── Test with production-like data
└── QA testing

PRODUCTION
├── Push to main branch
├── Render auto-deploys
├── Runs migrations
├── Health check
└── Live!
```

## Cost Breakdown

```
┌─────────────────────────────────────────────────────────────┐
│                     MONTHLY COSTS                            │
└─────────────────────────────────────────────────────────────┘

FREE TIER
├── Render Web Service: $0
├── Render PostgreSQL: $0
├── Render Redis: $0
├── Vercel Frontend: $0
├── Google OAuth: $0
├── Google Gemini: $0 (with limits)
└── TOTAL: $0/month

PRODUCTION TIER
├── Render Web Service: $7
├── Render PostgreSQL: $7
├── Render Redis: $10
├── Vercel Frontend: $0 (or $20 for Pro)
├── Google OAuth: $0
├── Google Gemini: ~$10-50 (usage-based)
├── Sentry: $0 (or $26 for Team)
└── TOTAL: $24-114/month
```

---

**Ready to deploy?** Follow the guides in order:
1. `RENDER_QUICK_START.md` - Get started in 15 minutes
2. `DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist
3. `RENDER_DEPLOYMENT_GUIDE.md` - Detailed documentation
