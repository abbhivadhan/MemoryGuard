# Celery Setup for ML Processing

This document describes how to set up and run Celery workers for asynchronous ML prediction processing.

## Overview

Celery is used to process ML predictions asynchronously, allowing the API to respond quickly while predictions are computed in the background.

## Architecture

- **Broker**: Redis (stores task queue)
- **Backend**: Redis (stores task results)
- **Workers**: Python processes that execute ML tasks
- **Tasks**: ML predictions, explanations, forecasts

## Prerequisites

1. Redis must be running
2. Python dependencies installed (celery, redis)

## Configuration

Celery is configured in `app/core/celery_app.py` with the following settings:

```python
CELERY_BROKER_URL = "redis://redis:6379/1"
CELERY_RESULT_BACKEND = "redis://redis:6379/2"
```

Update these in your `.env` file if needed:

```bash
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

## Running Celery Worker

### Development

Start a Celery worker with:

```bash
cd backend
celery -A celery_worker worker --loglevel=info
```

### With Auto-reload (Development)

For development with auto-reload on code changes:

```bash
watchmedo auto-restart --directory=./app --pattern=*.py --recursive -- celery -A celery_worker worker --loglevel=info
```

### Production

For production, use multiple workers and configure concurrency:

```bash
celery -A celery_worker worker \
  --loglevel=info \
  --concurrency=4 \
  --max-tasks-per-child=1000 \
  --time-limit=1800 \
  --soft-time-limit=1500
```

## Available Tasks

### 1. Process Prediction

**Task**: `ml.process_prediction`

Processes a single ML prediction asynchronously.

```python
from app.tasks.ml_tasks import process_prediction_task

result = process_prediction_task.delay(
    prediction_id=1,
    user_id=123,
    health_metrics={"mmse_score": 24, "age": 72}
)
```

### 2. Batch Predictions

**Task**: `ml.batch_predictions`

Processes predictions for multiple users.

```python
from app.tasks.ml_tasks import batch_predictions_task

result = batch_predictions_task.delay(
    user_ids=[1, 2, 3],
    health_metrics_list=[{...}, {...}, {...}]
)
```

### 3. Generate Explanation

**Task**: `ml.generate_explanation`

Generates SHAP explanation for a prediction.

```python
from app.tasks.ml_tasks import generate_explanation_task

result = generate_explanation_task.delay(prediction_id=1)
```

### 4. Update Forecasts

**Task**: `ml.update_forecasts`

Updates progression forecasts for a user.

```python
from app.tasks.ml_tasks import update_forecasts_task

result = update_forecasts_task.delay(user_id=123)
```

## Monitoring

### Flower (Web-based Monitoring)

Install Flower:

```bash
pip install flower
```

Run Flower:

```bash
celery -A celery_worker flower --port=5555
```

Access at: http://localhost:5555

### Command Line Monitoring

Check active workers:

```bash
celery -A celery_worker inspect active
```

Check registered tasks:

```bash
celery -A celery_worker inspect registered
```

Check worker stats:

```bash
celery -A celery_worker inspect stats
```

## Task Results

Get task result:

```python
from app.core.celery_app import celery_app

result = celery_app.AsyncResult(task_id)
print(result.state)  # PENDING, STARTED, SUCCESS, FAILURE
print(result.result)  # Task return value
```

## Error Handling

Tasks are configured with automatic retries:

- **Max retries**: 3
- **Retry delay**: 60 seconds
- **Time limit**: 30 minutes
- **Soft time limit**: 25 minutes

Failed tasks are logged and marked in the database.

## Docker Setup

Add Celery worker to `docker-compose.yml`:

```yaml
celery-worker:
  build: ./backend
  command: celery -A celery_worker worker --loglevel=info
  volumes:
    - ./backend:/app
  depends_on:
    - redis
    - postgres
  environment:
    - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/memoryguard
    - CELERY_BROKER_URL=redis://redis:6379/1
    - CELERY_RESULT_BACKEND=redis://redis:6379/2
```

## Scaling

### Multiple Workers

Run multiple worker processes:

```bash
# Terminal 1
celery -A celery_worker worker --loglevel=info -n worker1@%h

# Terminal 2
celery -A celery_worker worker --loglevel=info -n worker2@%h
```

### Queue Routing

Configure different queues for different task types:

```python
# In celery_app.py
celery_app.conf.task_routes = {
    'ml.process_prediction': {'queue': 'predictions'},
    'ml.batch_predictions': {'queue': 'batch'},
    'ml.generate_explanation': {'queue': 'explanations'},
}
```

Start workers for specific queues:

```bash
# Prediction worker
celery -A celery_worker worker -Q predictions --loglevel=info

# Batch worker
celery -A celery_worker worker -Q batch --loglevel=info
```

## Troubleshooting

### Worker Not Starting

1. Check Redis is running:
   ```bash
   redis-cli ping
   ```

2. Check broker URL is correct in config

3. Check for import errors:
   ```bash
   python -c "from app.core.celery_app import celery_app"
   ```

### Tasks Not Processing

1. Check worker is running and connected
2. Check task is registered:
   ```bash
   celery -A celery_worker inspect registered
   ```
3. Check task queue:
   ```bash
   redis-cli -n 1 LLEN celery
   ```

### Memory Issues

1. Reduce worker concurrency
2. Set max-tasks-per-child to restart workers periodically
3. Monitor memory usage with Flower

## Best Practices

1. **Always use `.delay()` or `.apply_async()`** to queue tasks asynchronously
2. **Keep tasks idempotent** - safe to retry
3. **Use task time limits** to prevent hanging tasks
4. **Monitor task queue length** to detect bottlenecks
5. **Log task progress** for debugging
6. **Handle failures gracefully** with retries and error logging

## References

- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)
- [Flower Documentation](https://flower.readthedocs.io/)
