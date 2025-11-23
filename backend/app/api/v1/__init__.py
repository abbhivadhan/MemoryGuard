"""
API v1 routes initialization.
"""
from fastapi import APIRouter
from app.api.v1 import auth, health, ml, assessments, reminders, routines, faces, medications, emergency, caregivers, exercises, recommendations, community, imaging, providers, rate_limits, gemini

# Create main v1 router
api_router = APIRouter()

# Include all v1 routers
api_router.include_router(auth.router)
api_router.include_router(health.router)
api_router.include_router(ml.router)
api_router.include_router(assessments.router)
api_router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
api_router.include_router(routines.router, prefix="/routines", tags=["routines"])
api_router.include_router(faces.router, prefix="/faces", tags=["face-recognition"])
api_router.include_router(medications.router, prefix="/medications", tags=["medications"])
api_router.include_router(emergency.router, prefix="/emergency", tags=["emergency"])
api_router.include_router(caregivers.router, prefix="/caregivers", tags=["caregivers"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["exercises"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(community.router, prefix="/community", tags=["community"])
api_router.include_router(imaging.router, prefix="/imaging", tags=["imaging"])
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
api_router.include_router(rate_limits.router)
api_router.include_router(gemini.router)

__all__ = ["api_router"]
