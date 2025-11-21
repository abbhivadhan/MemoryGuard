# MemoryGuard Design Document

## Overview

MemoryGuard is a full-stack web application that combines advanced machine learning for Alzheimer's early detection with comprehensive daily assistance features. The application uses a modern tech stack with React + Three.js for immersive 3D frontend experiences and Python FastAPI for robust ML-powered backend services.

### Core Value Proposition

- **Early Detection**: ML ensemble models analyzing biomedical data for risk assessment
- **Daily Assistance**: Memory aids, reminders, and routine tracking for independence
- **Health Monitoring**: Comprehensive tracking of cognitive, biomarker, and lifestyle metrics
- **Community Support**: Connection with others and access to resources
- **Clinical Integration**: Healthcare provider portal and medical data analysis

### Technology Stack

**Frontend:**
- React 18 with TypeScript
- Three.js with React Three Fiber for 3D rendering
- React Three Drei for 3D helpers
- Cannon.js for physics simulation
- Zustand for state management
- React Query for server state
- Tailwind CSS for styling
- Framer Motion for 2D animations
- Recharts for data visualization

**Backend:**
- Python 3.11+
- FastAPI for REST API
- SQLAlchemy for ORM
- PostgreSQL for database
- Redis for caching and sessions
- Celery for background tasks
- scikit-learn, XGBoost, TensorFlow for ML models
- SHAP for model interpretability
- PyDICOM for medical imaging
- Alembic for database migrations

**Authentication:**
- Google OAuth 2.0
- JWT tokens for session management

**Deployment:**
- Docker & Docker Compose
- Nginx as reverse proxy
- GitHub Actions for CI/CD
- AWS/GCP for hosting (configurable)

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 3D Homepage  │  │  Dashboard   │  │ Memory Tools │      │
│  │ (Three.js)   │  │  (3D Viz)    │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                    HTTPS/WebSocket
                            │
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Auth       │  │   ML API     │  │  Health API  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│   PostgreSQL   │  │    Redis    │  │  ML Services    │
│   (Primary DB) │  │   (Cache)   │  │  (Celery)       │
└────────────────┘  └─────────────┘  └─────────────────┘
```

### Frontend Architecture

**Component Structure:**

```
src/
├── components/
│   ├── 3d/
│   │   ├── BrainModel.tsx          # 3D brain visualization
│   │   ├── ParticleSystem.tsx      # Physics-based particles
│   │   ├── PhysicsButton.tsx       # Interactive 3D buttons
│   │   └── Scene.tsx               # Main 3D scene wrapper
│   ├── auth/
│   │   ├── GoogleAuthButton.tsx
│   │   └── ProtectedRoute.tsx
│   ├── dashboard/
│   │   ├── HealthMetrics.tsx       # 3D health visualizations
│   │   ├── RiskAssessment.tsx      # ML prediction display
│   │   └── ProgressionChart.tsx    # Timeline visualization
│   ├── memory/
│   │   ├── ReminderCard.tsx
│   │   ├── FaceRecognition.tsx
│   │   └── DailyRoutine.tsx
│   └── cognitive/
│       ├── MMSETest.tsx
│       ├── MoCATest.tsx
│       └── ClockDrawing.tsx
├── pages/
│   ├── HomePage.tsx                # 3D animated landing
│   ├── DashboardPage.tsx
│   ├── AssessmentPage.tsx
│   ├── CommunityPage.tsx
│   └── ProviderPortal.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useMLPrediction.ts
│   └── use3DPhysics.ts
├── store/
│   ├── authStore.ts
│   ├── healthStore.ts
│   └── uiStore.ts
└── services/
    ├── api.ts
    ├── mlService.ts
    └── authService.ts
```

### Backend Architecture

**Service Structure:**

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py             # Google OAuth endpoints
│   │   │   ├── ml.py               # ML prediction endpoints
│   │   │   ├── health.py           # Health metrics CRUD
│   │   │   ├── assessments.py      # Cognitive tests
│   │   │   ├── medications.py      # Medication tracking
│   │   │   ├── imaging.py          # MRI upload/analysis
│   │   │   └── community.py        # Forum endpoints
│   ├── core/
│   │   ├── config.py               # Environment config
│   │   ├── security.py             # JWT, encryption
│   │   └── database.py             # DB connection
│   ├── models/
│   │   ├── user.py
│   │   ├── health_metric.py
│   │   ├── assessment.py
│   │   ├── medication.py
│   │   └── prediction.py
│   ├── ml/
│   │   ├── models/
│   │   │   ├── ensemble.py         # Ensemble predictor
│   │   │   ├── random_forest.py
│   │   │   ├── xgboost_model.py
│   │   │   └── neural_net.py
│   │   ├── preprocessing.py        # Feature engineering
│   │   ├── interpretability.py     # SHAP explanations
│   │   └── imaging_analysis.py     # MRI processing
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── ml_service.py
│   │   ├── notification_service.py
│   │   └── imaging_service.py
│   └── tasks/
│       ├── ml_training.py          # Celery tasks
│       └── data_sync.py
├── alembic/                        # DB migrations
├── tests/
└── requirements.txt
```

## Components and Interfaces

### 1. 3D Homepage Component

**Purpose:** Immersive landing page that educates visitors about Alzheimer's and the app's mission

**3D Elements:**

- **Animated Brain Model**: 3D brain with particle effects showing neural connections fading (representing memory loss)
- **Physics-Based Particles**: Floating memory fragments that respond to mouse movement with gravity and collision
- **Interactive Journey**: Scroll-triggered animations showing disease progression and solution
- **Call-to-Action**: 3D button with physics hover effects leading to sign-up

**Technical Implementation:**
- React Three Fiber for 3D rendering
- Cannon.js for physics simulation
- GLTF models for brain anatomy
- Custom shaders for visual effects
- Intersection Observer for scroll animations

### 2. ML Prediction System

**Ensemble Model Architecture:**

```python
class AlzheimerEnsemble:
    models = [
        RandomForestClassifier(n_estimators=200),
        XGBClassifier(max_depth=6),
        KerasNeuralNetwork(layers=[128, 64, 32])
    ]
    
    def predict(self, features):
        predictions = [model.predict_proba(features) for model in self.models]
        return weighted_average(predictions)
```

**Input Features:**
- Cognitive scores (MMSE, MoCA, CDR)
- Biomarkers (Aβ42, t-Tau, p-Tau ratios)
- MRI volumetrics (hippocampus, entorhinal cortex)
- Demographics (age, education, APOE status)
- Lifestyle (exercise, diet, sleep, social engagement)

**Output:**
- Risk probability (0-1 scale)
- Confidence interval
- SHAP feature importance
- Progression timeline forecast

### 3. Health Metrics Dashboard

**3D Visualizations:**
- Brain health sphere with color-coded regions
- Biomarker levels as 3D bar charts with physics
- Timeline visualization with animated progression curve
- Interactive 3D scatter plots for correlations

**Metrics Tracked:**
- Cognitive: MMSE (0-30), MoCA (0-30), CDR (0-3)
- Biomarkers: CSF levels, blood markers
- Brain: Hippocampal volume, cortical thickness
- Lifestyle: Activity minutes, sleep hours, social interactions
- Cardiovascular: BP, cholesterol, glucose

### 4. Cognitive Assessment Engine

**Digital Tests:**

**MMSE (Mini-Mental State Examination):**
- Orientation (10 points)
- Registration (3 points)
- Attention & Calculation (5 points)
- Recall (3 points)
- Language (9 points)

**MoCA (Montreal Cognitive Assessment):**
- Visuospatial/Executive (5 points)
- Naming (3 points)
- Memory (5 points)
- Attention (6 points)
- Language (3 points)
- Abstraction (2 points)
- Delayed Recall (5 points)
- Orientation (6 points)

**Implementation:**
- Interactive 3D interfaces for each test component
- Audio instructions with text-to-speech
- Automatic scoring algorithms
- Progress saving for incomplete tests

### 5. Memory Assistant Features

**Reminder System:**
- Medication reminders with visual + audio alerts
- Appointment notifications
- Daily routine checklist
- Custom reminders

**Face Recognition:**
- Upload photos of family/friends with names
- Camera-based recognition using TensorFlow.js
- Relationship context and memory prompts

**Daily Routine Tracker:**
- Morning, afternoon, evening routines
- Visual progress indicators with 3D animations
- Completion streaks and encouragement

### 6. Emergency Response System

**Features:**
- Prominent SOS button on all screens
- GPS location sharing
- Emergency contact auto-notification
- Medical information card
- Safe return home navigation
- Pattern detection (missed meds, incomplete routines)

**Alert Triggers:**
- Manual SOS activation
- Medication adherence < 80% for 7 days
- Missed 3+ daily routine items
- Cognitive test score decline > 20%
- No app activity for 48 hours

## Data Models

### User Model
```typescript
interface User {
  id: string;
  email: string;
  name: string;
  dateOfBirth: Date;
  apoeGenotype?: 'e2/e2' | 'e2/e3' | 'e2/e4' | 'e3/e3' | 'e3/e4' | 'e4/e4';
  emergencyContacts: EmergencyContact[];
  caregivers: string[]; // User IDs
  providers: string[]; // Provider IDs
  createdAt: Date;
  lastActive: Date;
}
```

### Health Metric Model
```typescript
interface HealthMetric {
  id: string;
  userId: string;
  type: 'cognitive' | 'biomarker' | 'imaging' | 'lifestyle' | 'cardiovascular';
  name: string;
  value: number;
  unit: string;
  timestamp: Date;
  source: 'manual' | 'assessment' | 'device' | 'lab';
}
```

### Assessment Model
```typescript
interface Assessment {
  id: string;
  userId: string;
  type: 'MMSE' | 'MoCA' | 'CDR' | 'ClockDrawing';
  score: number;
  maxScore: number;
  responses: Record<string, any>;
  duration: number; // seconds
  completedAt: Date;
}
```

### Prediction Model
```typescript
interface Prediction {
  id: string;
  userId: string;
  riskScore: number; // 0-1
  confidenceInterval: [number, number];
  riskCategory: 'low' | 'moderate' | 'high';
  featureImportance: Record<string, number>;
  progressionForecast: {
    sixMonth: number;
    twelveMonth: number;
    twentyFourMonth: number;
  };
  recommendations: string[];
  createdAt: Date;
}
```

### Medication Model
```typescript
interface Medication {
  id: string;
  userId: string;
  name: string;
  dosage: string;
  frequency: string;
  schedule: Date[];
  adherenceLog: {
    scheduledTime: Date;
    takenTime?: Date;
    skipped: boolean;
  }[];
  sideEffects: string[];
  active: boolean;
}
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/google` - Google OAuth callback
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `POST /api/v1/auth/logout` - Invalidate session

### ML Predictions
- `POST /api/v1/ml/predict` - Generate risk prediction
- `GET /api/v1/ml/predictions/:userId` - Get prediction history
- `GET /api/v1/ml/explain/:predictionId` - Get SHAP explanations

### Health Metrics
- `POST /api/v1/health/metrics` - Add health metric
- `GET /api/v1/health/metrics/:userId` - Get all metrics
- `GET /api/v1/health/metrics/:userId/:type` - Get metrics by type
- `PUT /api/v1/health/metrics/:id` - Update metric
- `DELETE /api/v1/health/metrics/:id` - Delete metric

### Assessments
- `POST /api/v1/assessments/start` - Start new assessment
- `PUT /api/v1/assessments/:id/response` - Save response
- `POST /api/v1/assessments/:id/complete` - Complete and score
- `GET /api/v1/assessments/:userId` - Get assessment history

### Medications
- `POST /api/v1/medications` - Add medication
- `GET /api/v1/medications/:userId` - Get all medications
- `POST /api/v1/medications/:id/log` - Log medication taken
- `GET /api/v1/medications/:id/adherence` - Get adherence stats

### Imaging
- `POST /api/v1/imaging/upload` - Upload MRI DICOM
- `GET /api/v1/imaging/:id/analysis` - Get analysis results
- `GET /api/v1/imaging/:userId` - Get all imaging studies

### Community
- `GET /api/v1/community/posts` - Get forum posts
- `POST /api/v1/community/posts` - Create post
- `POST /api/v1/community/posts/:id/reply` - Reply to post

## Error Handling

### Frontend Error Boundaries
- Global error boundary for React crashes
- 3D scene error fallback to 2D interface
- Network error retry logic with exponential backoff
- User-friendly error messages

### Backend Error Responses
```json
{
  "error": {
    "code": "PREDICTION_FAILED",
    "message": "Unable to generate prediction",
    "details": "Insufficient input features",
    "timestamp": "2025-11-15T10:30:00Z"
  }
}
```

### Error Categories
- `400` - Validation errors
- `401` - Authentication errors
- `403` - Authorization errors
- `404` - Resource not found
- `429` - Rate limit exceeded
- `500` - Server errors
- `503` - Service unavailable

## Testing Strategy

### Frontend Testing
- **Unit Tests**: Jest + React Testing Library for components
- **Integration Tests**: Test user flows (auth, assessment completion)
- **3D Rendering Tests**: Mock Three.js for component logic
- **E2E Tests**: Playwright for critical paths
- **Accessibility Tests**: axe-core for WCAG compliance

### Backend Testing
- **Unit Tests**: pytest for individual functions
- **Integration Tests**: Test API endpoints with test database
- **ML Model Tests**: Validate predictions on test dataset
- **Load Tests**: Locust for performance testing
- **Security Tests**: OWASP ZAP for vulnerability scanning

### Test Coverage Goals
- Frontend: > 80% coverage
- Backend: > 85% coverage
- ML Models: > 90% accuracy on validation set

## Performance Optimization

### Frontend
- Code splitting by route
- Lazy loading for 3D models
- WebGL optimization (LOD, frustum culling)
- Service worker for offline caching
- Image optimization (WebP, lazy loading)
- Debounced API calls

### Backend
- Redis caching for frequent queries
- Database indexing on common queries
- Connection pooling
- Async processing for ML predictions
- CDN for static assets
- Response compression (gzip)

### ML Model Optimization
- Model quantization for faster inference
- Feature caching
- Batch prediction support
- Model versioning for A/B testing

## Security Considerations

### Authentication & Authorization
- JWT with short expiration (15 min access, 7 day refresh)
- HTTP-only cookies for tokens
- CSRF protection
- Role-based access control (patient, caregiver, provider)

### Data Protection
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- HIPAA compliance measures
- PHI data anonymization for analytics
- Audit logging for all data access

### API Security
- Rate limiting (100 req/min per user)
- Input validation and sanitization
- SQL injection prevention (parameterized queries)
- XSS protection (Content Security Policy)
- CORS configuration

## Deployment Architecture

### Docker Containers
- `frontend`: Nginx serving React build
- `backend`: Gunicorn + FastAPI
- `postgres`: PostgreSQL 15
- `redis`: Redis 7
- `celery-worker`: Background tasks
- `celery-beat`: Scheduled tasks

### Environment Configuration
```yaml
# docker-compose.yml
services:
  frontend:
    build: ./frontend
    ports: ["3000:80"]
    environment:
      - REACT_APP_API_URL=${API_URL}
      - REACT_APP_GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
  
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
    depends_on:
      - postgres
      - redis
```

### CI/CD Pipeline
1. **Build**: Install dependencies, run linters
2. **Test**: Run unit and integration tests
3. **Build Docker Images**: Create production images
4. **Deploy to Staging**: Automated deployment
5. **Run E2E Tests**: Validate staging environment
6. **Deploy to Production**: Manual approval required
7. **Health Checks**: Verify deployment success

### Monitoring & Logging
- Application logs: Winston (frontend), Python logging (backend)
- Error tracking: Sentry
- Performance monitoring: New Relic or DataDog
- Uptime monitoring: UptimeRobot
- Log aggregation: ELK stack or CloudWatch

## Accessibility

### WCAG 2.1 AA Compliance
- Keyboard navigation for all features
- Screen reader support with ARIA labels
- Color contrast ratios > 4.5:1
- Text alternatives for 3D visualizations
- Captions for audio instructions
- Resizable text up to 200%

### Cognitive Accessibility
- Simple, clear language
- Consistent navigation patterns
- Visual cues for important actions
- Undo functionality for critical actions
- Progress indicators for multi-step processes

## Future Enhancements

### Phase 2 Features
- Voice assistant integration (Alexa, Google Home)
- Wearable device integration (Apple Watch, Fitbit)
- Telemedicine video consultations
- AI chatbot for 24/7 support
- Multi-language support
- Mobile native apps (React Native)

### ML Model Improvements
- Federated learning for privacy-preserving training
- Real-time progression monitoring
- Personalized intervention recommendations
- Integration with electronic health records (EHR)
- Clinical trial matching

## Design Decisions & Rationale

### Why Three.js + React Three Fiber?
- Industry-standard WebGL library
- React integration for component-based 3D
- Large ecosystem and community support
- Performance optimization built-in

### Why FastAPI?
- Modern Python framework with async support
- Automatic OpenAPI documentation
- Type hints for better code quality
- Fast performance comparable to Node.js

### Why PostgreSQL?
- ACID compliance for healthcare data
- JSON support for flexible schemas
- Strong ecosystem and tooling
- Proven reliability at scale

### Why Ensemble ML Models?
- Higher accuracy than single models
- Reduced overfitting risk
- Captures different aspects of disease
- Robust to individual model failures

This design provides a comprehensive, production-ready architecture for MemoryGuard that addresses all requirements while maintaining scalability, security, and user experience excellence.
