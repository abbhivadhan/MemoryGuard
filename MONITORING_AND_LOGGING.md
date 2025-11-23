# Monitoring and Logging Implementation

This document describes the comprehensive monitoring and logging system implemented for MemoryGuard.

## Overview

The monitoring and logging system provides:
- **Structured Logging**: JSON-formatted logs for production, colored logs for development
- **Error Tracking**: Sentry integration for error monitoring and alerting
- **Health Checks**: Multiple health check endpoints for container orchestration
- **Performance Monitoring**: Real-time tracking of API response times, 3D rendering, and system resources

## Backend Logging

### Configuration

Logging is configured in `backend/app/core/logging_config.py`:

- **Development**: Colored console output with human-readable format
- **Production**: JSON-formatted logs for easy parsing and analysis
- **File Logging**: Separate files for all logs (`app.log`) and errors (`error.log`)

### Usage

```python
from app.core.logging_config import get_logger, LogContext, log_performance

logger = get_logger(__name__)

# Basic logging
logger.info("User logged in", extra={"user_id": "123"})
logger.error("Failed to process request", exc_info=True)

# With context
with LogContext(user_id="123", request_id="abc"):
    logger.info("Processing request")

# Performance logging decorator
@log_performance(logger)
async def my_function():
    pass
```

### Log Levels

- `DEBUG`: Detailed information for debugging
- `INFO`: General informational messages
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failures
- `CRITICAL`: Critical errors requiring immediate attention

## Frontend Logging

### Configuration

Logging is configured in `frontend/src/services/logger.ts` using Winston:

- **Console Transport**: Colored output for development
- **Backend Transport**: Sends logs to backend in production
- **LocalStorage Transport**: Stores last 100 logs locally for offline debugging

### Usage

```typescript
import logger, { logError, logPerformance, logUserAction, logAPICall } from './services/logger';

// Basic logging
logger.info('User action', { action: 'button_click' });
logger.error('API call failed', { endpoint: '/api/users' });

// Helper functions
logError('Failed to load data', error, { component: 'Dashboard' });
logPerformance('Data fetch', 1234, { endpoint: '/api/data' });
logUserAction('Clicked submit button', { form: 'login' });
logAPICall('GET', '/api/users', 200, 456);
```

## Error Tracking (Sentry)

### Backend Configuration

Sentry is configured in `backend/app/core/sentry_config.py`:

```python
from app.core.sentry_config import capture_exception, capture_message, set_user_context

# Capture exception
try:
    risky_operation()
except Exception as e:
    capture_exception(e, context={"operation": "data_processing"})

# Capture message
capture_message("Important event occurred", level="info")

# Set user context
set_user_context(user_id="123", email="user@example.com")
```

### Frontend Configuration

Sentry is configured in `frontend/src/services/sentry.ts`:

```typescript
import { captureException, captureMessage, setUserContext } from './services/sentry';

// Capture exception
try {
  riskyOperation();
} catch (error) {
  captureException(error, { component: 'Dashboard' });
}

// Capture message
captureMessage('User completed onboarding', 'info');

// Set user context
setUserContext('user-123', 'user@example.com');
```

### Environment Variables

**Backend (.env):**
```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENABLED=true
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```

**Frontend (.env):**
```bash
VITE_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
VITE_SENTRY_ENABLED=true
VITE_SENTRY_TRACES_SAMPLE_RATE=0.1
```

### Privacy & HIPAA Compliance

Both backend and frontend Sentry configurations include:
- **PII Filtering**: Automatic removal of sensitive data
- **PHI Protection**: Medical data is filtered before sending
- **Custom Filters**: `beforeSend` and `beforeBreadcrumb` hooks filter sensitive information

Sensitive patterns filtered:
- Passwords, tokens, API keys
- Medical records, health metrics, biomarkers
- Medications, diagnoses, assessments
- SSN, medical record numbers

## Health Check Endpoints

### Available Endpoints

#### 1. Basic Health Check
```
GET /api/v1/health
```

Returns overall system health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1700000000.0,
  "environment": "production",
  "version": "0.1.0",
  "response_time_ms": 12.34,
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

#### 2. Detailed Health Check
```
GET /api/v1/health/detailed
```

Comprehensive health information including system resources and ML models.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1700000000.0,
  "checks": {
    "database": {
      "status": "healthy",
      "latency_ms": 5.23
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 1.45,
      "info": {
        "used_memory_human": "2.5M",
        "connected_clients": 3
      }
    },
    "ml_models": {
      "status": "healthy",
      "production_version": "v1.0.0",
      "total_models": 3
    },
    "system_resources": {
      "status": "healthy",
      "cpu_percent": 25.5,
      "memory_percent": 45.2,
      "disk_percent": 60.1
    }
  }
}
```

#### 3. Readiness Check (Kubernetes)
```
GET /api/v1/health/ready
```

Returns 200 if service is ready to accept traffic.

#### 4. Liveness Check (Kubernetes)
```
GET /api/v1/health/live
```

Returns 200 if service is alive.

#### 5. Startup Check (Kubernetes)
```
GET /api/v1/health/startup
```

Returns 200 when service has completed initialization.

#### 6. Performance Metrics
```
GET /api/v1/health/metrics
```

Returns performance metrics for monitoring.

**Response:**
```json
{
  "time_window_seconds": 300,
  "timestamp": 1700000000.0,
  "endpoints": {
    "/api/v1/users": {
      "sample_count": 150,
      "error_rate": 0.02,
      "duration_ms": {
        "min": 10.5,
        "max": 250.3,
        "mean": 45.2,
        "median": 42.1,
        "p95": 120.5,
        "p99": 200.1
      }
    }
  },
  "database": {
    "SELECT": {
      "sample_count": 500,
      "mean_ms": 15.3,
      "median_ms": 12.1
    }
  },
  "ml_models": {
    "ensemble_predictor": {
      "sample_count": 25,
      "success_rate": 0.96,
      "mean_ms": 1234.5
    }
  }
}
```

## Performance Monitoring

### Backend Performance

Performance monitoring is implemented in `backend/app/core/performance_monitor.py`:

```python
from app.core.performance_monitor import performance_metrics, track_performance

# Automatic tracking via middleware (already configured)
# All API requests are automatically tracked

# Manual tracking
@track_performance("ml")
async def predict_risk(data):
    # ML inference code
    pass

# Get statistics
stats = performance_metrics.get_endpoint_stats("/api/v1/predict")
```

### Frontend Performance

Performance monitoring is implemented in `frontend/src/hooks/usePerformance.ts`:

```typescript
import { usePerformance } from './hooks/usePerformance';

function MyComponent() {
  const { metrics, threeDMetrics, track3DPerformance, measureRender } = usePerformance();
  
  // Track 3D rendering
  useEffect(() => {
    if (renderer) {
      track3DPerformance('main-scene', renderer);
    }
  }, [renderer]);
  
  // Measure component render
  measureRender('MyComponent', () => {
    // Render logic
  });
  
  return (
    <div>
      <p>FPS: {metrics.fps}</p>
      <p>LCP: {metrics.largestContentfulPaint}ms</p>
    </div>
  );
}
```

### Performance Monitor Component

A visual performance monitor is available for development:

```typescript
import { PerformanceMonitor } from './components/utils/PerformanceMonitor';

function App() {
  return (
    <>
      <PerformanceMonitor enabled={true} position="bottom-right" />
      {/* Your app */}
    </>
  );
}
```

### Core Web Vitals Tracked

- **LCP (Largest Contentful Paint)**: Target < 2.5s
- **FID (First Input Delay)**: Target < 100ms
- **CLS (Cumulative Layout Shift)**: Target < 0.1
- **FPS (Frames Per Second)**: Target > 30fps
- **Memory Usage**: Monitored for leaks

### 3D Rendering Metrics

- Draw calls per frame
- Triangle count
- Geometry count
- Texture count
- FPS during 3D rendering

## Monitoring Best Practices

### 1. Log Levels

- Use `DEBUG` for detailed debugging information
- Use `INFO` for normal operations
- Use `WARNING` for potential issues
- Use `ERROR` for failures that need attention
- Use `CRITICAL` for system-critical failures

### 2. Structured Logging

Always include context in logs:

```python
logger.info("User action", extra={
    "user_id": user_id,
    "action": "login",
    "ip_address": request.client.host
})
```

### 3. Performance Thresholds

Monitor and alert on:
- API response time > 1000ms
- Database query time > 100ms
- ML inference time > 5000ms
- FPS < 30
- Memory usage > 500MB
- Error rate > 5%

### 4. Health Check Integration

Configure your orchestration platform:

**Kubernetes:**
```yaml
livenessProbe:
  httpGet:
    path: /api/v1/health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/v1/health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5

startupProbe:
  httpGet:
    path: /api/v1/health/startup
    port: 8000
  failureThreshold: 30
  periodSeconds: 10
```

**Docker Compose:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Troubleshooting

### High Memory Usage

1. Check `/api/v1/health/detailed` for memory stats
2. Review logs for memory warnings
3. Check for memory leaks in 3D scenes
4. Monitor texture and geometry disposal

### Slow API Responses

1. Check `/api/v1/health/metrics` for endpoint stats
2. Review database query performance
3. Check Redis connection latency
4. Monitor ML inference times

### Low FPS

1. Use PerformanceMonitor component to identify issues
2. Check draw calls and triangle count
3. Review 3D scene complexity
4. Consider implementing LOD (Level of Detail)

### Missing Logs

1. Verify log level configuration
2. Check file permissions for log files
3. Ensure Redis is connected for distributed logging
4. Verify Sentry DSN is configured correctly

## Dependencies

### Backend
- `psutil>=5.9.0` - System resource monitoring
- `sentry-sdk[fastapi]>=2.0.0` - Error tracking

### Frontend
- `winston` - Logging library
- `winston-transport` - Custom transports
- `@sentry/react` - Error tracking
- `@sentry/tracing` - Performance monitoring

## Next Steps

1. **Set up Sentry Projects**: Create projects in Sentry for frontend and backend
2. **Configure Alerts**: Set up alerts for error rates, performance degradation
3. **Dashboard**: Create monitoring dashboards (Grafana, DataDog, etc.)
4. **Log Aggregation**: Set up centralized logging (ELK stack, CloudWatch, etc.)
5. **APM**: Consider Application Performance Monitoring tools
6. **Synthetic Monitoring**: Set up uptime monitoring and synthetic tests

## References

- [Sentry Documentation](https://docs.sentry.io/)
- [Winston Documentation](https://github.com/winstonjs/winston)
- [Core Web Vitals](https://web.dev/vitals/)
- [Kubernetes Health Checks](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
