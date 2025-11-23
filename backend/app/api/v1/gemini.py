"""
Gemini AI API endpoints for health insights and conversational assistance
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import logging

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.gemini_service import get_gemini_service, GeminiRateLimitError, GeminiAPIError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gemini", tags=["gemini"])


# Request/Response Models
class HealthInsightsRequest(BaseModel):
    """Request for health insights generation"""
    user_data: Dict[str, Any] = Field(..., description="User health data for analysis")
    focus_areas: Optional[List[str]] = Field(None, description="Specific areas to focus on")


class HealthInsightsResponse(BaseModel):
    """Response with health insights"""
    insights: List[str]
    recommendations: List[str]
    warnings: List[str]
    next_steps: List[str]


class ChatRequest(BaseModel):
    """Request for conversational health assistant"""
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="Previous messages")
    user_context: Optional[Dict[str, Any]] = Field(None, description="User health context")


class ChatResponse(BaseModel):
    """Response from health assistant"""
    response: str
    conversation_id: Optional[str] = None


class AssessmentAnalysisRequest(BaseModel):
    """Request for cognitive assessment analysis"""
    assessment_type: str = Field(..., description="Type of assessment (MMSE, MoCA, etc.)")
    responses: Dict[str, Any] = Field(..., description="Assessment responses")
    score: int = Field(..., ge=0, description="Assessment score")
    max_score: int = Field(..., gt=0, description="Maximum possible score")


class AssessmentAnalysisResponse(BaseModel):
    """Response with assessment analysis"""
    feedback: str
    strengths: List[str]
    areas_for_improvement: List[str]
    suggestions: List[str]


class PredictionExplanationRequest(BaseModel):
    """Request for ML prediction explanation"""
    prediction_data: Dict[str, Any] = Field(..., description="ML prediction data")
    user_friendly: bool = Field(True, description="Use simple language")


class PredictionExplanationResponse(BaseModel):
    """Response with prediction explanation"""
    explanation: str


@router.post("/health-insights", response_model=HealthInsightsResponse)
async def generate_health_insights(
    request: HealthInsightsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate personalized health insights using Gemini AI.
    
    Analyzes user health data and provides evidence-based recommendations
    for maintaining cognitive health and reducing Alzheimer's risk.
    """
    try:
        gemini_service = get_gemini_service()
        
        if not gemini_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini AI service is not available. Please try again later."
            )
        
        # Generate insights
        result = gemini_service.generate_health_insights(
            user_data=request.user_data,
            focus_areas=request.focus_areas
        )
        
        # Log interaction
        gemini_service.log_interaction(
            interaction_type="health_insights",
            prompt_length=len(str(request.user_data)),
            response_length=len(str(result)),
            success=True
        )
        
        return HealthInsightsResponse(**result)
    
    except GeminiRateLimitError as e:
        logger.warning(f"Rate limit exceeded for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    except GeminiAPIError as e:
        logger.error(f"Gemini API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable. Please try again later."
        )
    
    except Exception as e:
        logger.error(f"Error generating health insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate health insights"
        )



@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Conversational health assistant powered by Gemini AI.
    
    Provides empathetic, context-aware responses to user questions
    about Alzheimer's disease, cognitive health, and daily living.
    """
    try:
        gemini_service = get_gemini_service()
        
        if not gemini_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Chat assistant is not available. Please try again later."
            )
        
        # Generate response
        response = gemini_service.chat(
            message=request.message,
            conversation_history=request.conversation_history,
            user_context=request.user_context
        )
        
        # Log interaction
        gemini_service.log_interaction(
            interaction_type="chat",
            prompt_length=len(request.message),
            response_length=len(response),
            success=True
        )
        
        return ChatResponse(response=response)
    
    except GeminiRateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@router.post("/analyze-assessment", response_model=AssessmentAnalysisResponse)
async def analyze_cognitive_assessment(
    request: AssessmentAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze cognitive assessment results using Gemini AI.
    
    Provides detailed feedback, identifies strengths, and suggests
    personalized improvement strategies.
    """
    try:
        gemini_service = get_gemini_service()
        
        if not gemini_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Assessment analysis is not available. Please try again later."
            )
        
        # Analyze assessment
        result = gemini_service.analyze_assessment(
            assessment_type=request.assessment_type,
            responses=request.responses,
            score=request.score,
            max_score=request.max_score
        )
        
        # Log interaction
        gemini_service.log_interaction(
            interaction_type="assessment_analysis",
            prompt_length=len(str(request.responses)),
            response_length=len(str(result)),
            success=True
        )
        
        return AssessmentAnalysisResponse(**result)
    
    except GeminiRateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    except Exception as e:
        logger.error(f"Error analyzing assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze assessment"
        )


@router.post("/explain-prediction", response_model=PredictionExplanationResponse)
async def explain_ml_prediction(
    request: PredictionExplanationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate plain-language explanation of ML prediction using Gemini AI.
    
    Translates technical ML outputs into understandable insights
    that help users make informed health decisions.
    """
    try:
        gemini_service = get_gemini_service()
        
        if not gemini_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Prediction explanation is not available. Please try again later."
            )
        
        # Generate explanation
        explanation = gemini_service.explain_ml_prediction(
            prediction_data=request.prediction_data,
            user_friendly=request.user_friendly
        )
        
        # Log interaction
        gemini_service.log_interaction(
            interaction_type="prediction_explanation",
            prompt_length=len(str(request.prediction_data)),
            response_length=len(explanation),
            success=True
        )
        
        return PredictionExplanationResponse(explanation=explanation)
    
    except GeminiRateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    except Exception as e:
        logger.error(f"Error explaining prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to explain prediction"
        )


@router.get("/status")
async def get_gemini_status(
    current_user: User = Depends(get_current_user)
):
    """
    Check Gemini AI service availability status.
    """
    gemini_service = get_gemini_service()
    return {
        "available": gemini_service.is_available(),
        "model": gemini_service.model_name if gemini_service.is_available() else None
    }
