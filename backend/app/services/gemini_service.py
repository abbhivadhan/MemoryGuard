"""
Google Gemini AI Service

Provides integration with Google's Gemini AI API for:
- Health insights generation
- Conversational health assistance
- Cognitive assessment analysis
- ML prediction explanations
"""

import logging
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
import re

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.redis import get_redis

logger = logging.getLogger(__name__)


class GeminiRateLimitError(Exception):
    """Raised when Gemini API rate limit is exceeded"""
    pass


class GeminiAPIError(Exception):
    """Raised when Gemini API returns an error"""
    pass


class GeminiService:
    """
    Service for interacting with Google Gemini AI API.
    Includes rate limiting, error handling, retry logic, and response caching.
    """
    
    def __init__(self):
        """Initialize Gemini AI service"""
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.max_tokens = settings.GEMINI_MAX_TOKENS
        self.temperature = settings.GEMINI_TEMPERATURE
        self.rate_limit = settings.GEMINI_RATE_LIMIT_PER_MINUTE
        self.timeout = settings.GEMINI_TIMEOUT_SECONDS
        self.max_retries = settings.GEMINI_MAX_RETRIES
        
        # Initialize the API
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                }
            )
            self._is_configured = True
            logger.info(f"Gemini AI service initialized with model: {self.model_name}")
        else:
            self._is_configured = False
            logger.warning("Gemini API key not configured. Service will use fallback responses.")
        
        self.redis = get_redis()
        self._rate_limit_key = "gemini:rate_limit"
        self._cache_prefix = "gemini:cache:"
    
    def is_available(self) -> bool:
        """Check if Gemini AI service is available"""
        return self._is_configured
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        if not self.redis:
            return True
        
        try:
            current_count = self.redis.get(self._rate_limit_key)
            if current_count is None:
                self.redis.setex(self._rate_limit_key, 60, 1)
                return True
            
            count = int(current_count)
            if count >= self.rate_limit:
                logger.warning(f"Gemini API rate limit exceeded: {count}/{self.rate_limit}")
                return False
            
            self.redis.incr(self._rate_limit_key)
            return True
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if available"""
        if not self.redis:
            return None
        
        try:
            cached = self.redis.get(f"{self._cache_prefix}{cache_key}")
            if cached:
                logger.info(f"Using cached Gemini response for key: {cache_key}")
                return cached.decode('utf-8') if isinstance(cached, bytes) else cached
        except Exception as e:
            logger.error(f"Error retrieving cached response: {e}")
        
        return None
    
    def _cache_response(self, cache_key: str, response: str, ttl: int = 3600):
        """Cache response for future use"""
        if not self.redis:
            return
        
        try:
            self.redis.setex(f"{self._cache_prefix}{cache_key}", ttl, response)
            logger.info(f"Cached Gemini response for key: {cache_key}")
        except Exception as e:
            logger.error(f"Error caching response: {e}")
    
    def _sanitize_input(self, text: str) -> str:
        """Sanitize user input before sending to Gemini AI"""
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        text = re.sub(r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', text)
        
        max_length = settings.MAX_INPUT_STRING_LENGTH
        if len(text) > max_length:
            text = text[:max_length] + "..."
            logger.warning(f"Input truncated to {max_length} characters")
        
        return text.strip()
    
    def _contains_pii(self, text: str) -> bool:
        """Check if text contains potential PII"""
        pii_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\b\d{3}-\d{2}-\d{4}\b',
        ]
        return any(re.search(pattern, text) for pattern in pii_patterns)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((GeminiAPIError, Exception)),
        reraise=True
    )
    def _generate_content(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate content using Gemini AI with retry logic"""
        if not self._is_configured:
            raise GeminiAPIError("Gemini AI is not configured")
        
        if not self._check_rate_limit():
            raise GeminiRateLimitError("Rate limit exceeded. Please try again later.")
        
        try:
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
            )
            
            logger.info(f"Gemini API call successful. Prompt length: {len(prompt)}")
            return response.text
        
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise GeminiAPIError(f"Failed to generate content: {str(e)}")
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from response text"""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"response": response_text}
        except json.JSONDecodeError:
            return {"response": response_text}
    
    def _fallback_health_insights(self) -> Dict[str, Any]:
        """Fallback response when Gemini is unavailable"""
        return {
            "insights": ["Gemini AI is currently unavailable. Please consult with your healthcare provider."],
            "recommendations": ["Maintain regular cognitive activities", "Stay physically active", "Get adequate sleep"],
            "warnings": ["This is a fallback response. For personalized insights, please try again later."],
            "next_steps": ["Consult with your healthcare provider for personalized recommendations"]
        }
    
    def _fallback_chat_response(self) -> str:
        """Fallback chat response"""
        return "I'm currently unavailable. Please consult with your healthcare provider for medical advice."
    
    def generate_health_insights(
        self,
        user_data: Dict[str, Any],
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate personalized health insights based on user data"""
        if not self.is_available():
            return self._fallback_health_insights()
        
        try:
            cache_key = f"health_insights:{hash(json.dumps(user_data, sort_keys=True))}"
            cached = self._get_cached_response(cache_key)
            if cached:
                return json.loads(cached)
            
            sanitized_data = {k: v for k, v in user_data.items() if not self._contains_pii(str(v))}
            
            system_instruction = """You are a medical AI assistant specializing in Alzheimer's disease.
Provide evidence-based insights. Include: insights, recommendations, warnings, next_steps.
Always remind users to consult healthcare professionals."""
            
            focus_text = f"Focus on: {', '.join(focus_areas)}" if focus_areas else ""
            prompt = f"""Analyze this health data:

{json.dumps(sanitized_data, indent=2)}

{focus_text}

Provide actionable recommendations for cognitive health."""
            
            response_text = self._generate_content(prompt, system_instruction)
            result = self._parse_json_response(response_text)
            self._cache_response(cache_key, json.dumps(result), ttl=3600)
            
            return result
        
        except Exception as e:
            logger.error(f"Error generating health insights: {e}")
            return self._fallback_health_insights()
    
    def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Conversational health assistant"""
        if not self.is_available():
            return self._fallback_chat_response()
        
        try:
            sanitized_message = self._sanitize_input(message)
            
            system_instruction = """You are a compassionate health assistant for Alzheimer's patients.
Use simple language. Be empathetic. Remind users to consult healthcare professionals.
Never diagnose or prescribe."""
            
            context_parts = []
            if conversation_history:
                for msg in conversation_history[-5:]:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    context_parts.append(f"{role}: {content}")
            
            if user_context:
                context_parts.append(f"Context: {json.dumps(user_context)}")
            
            context_text = "\n".join(context_parts) if context_parts else ""
            prompt = f"{context_text}\n\nUser: {sanitized_message}\n\nAssistant:"
            
            response = self._generate_content(prompt, system_instruction)
            return response
        
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return self._fallback_chat_response()
    
    def analyze_assessment(
        self,
        assessment_type: str,
        responses: Dict[str, Any],
        score: int,
        max_score: int
    ) -> Dict[str, Any]:
        """Analyze cognitive assessment and provide feedback"""
        if not self.is_available():
            return {
                "feedback": "Assessment analysis unavailable. Please consult your healthcare provider.",
                "strengths": [],
                "areas_for_improvement": [],
                "suggestions": []
            }
        
        try:
            system_instruction = """You are a cognitive assessment specialist.
Analyze assessment results and provide constructive feedback.
Focus on strengths and gentle suggestions for improvement."""
            
            prompt = f"""Assessment: {assessment_type}
Score: {score}/{max_score}
Responses: {json.dumps(responses, indent=2)}

Provide detailed feedback with strengths, areas for improvement, and suggestions."""
            
            response_text = self._generate_content(prompt, system_instruction)
            result = self._parse_json_response(response_text)
            
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing assessment: {e}")
            return {"feedback": "Analysis unavailable", "strengths": [], "areas_for_improvement": [], "suggestions": []}
    
    def explain_ml_prediction(
        self,
        prediction_data: Dict[str, Any],
        user_friendly: bool = True
    ) -> str:
        """Generate plain-language explanation of ML prediction"""
        if not self.is_available():
            return "Prediction explanation unavailable. Please consult your healthcare provider."
        
        try:
            system_instruction = """You are an AI explainability specialist.
Translate technical ML outputs into clear, understandable language.
Focus on what the prediction means and what actions to take."""
            
            complexity = "simple, non-technical" if user_friendly else "detailed"
            prompt = f"""Explain this ML prediction in {complexity} language:

{json.dumps(prediction_data, indent=2)}

Help the user understand what this means for their health."""
            
            response = self._generate_content(prompt, system_instruction)
            return response
        
        except Exception as e:
            logger.error(f"Error explaining prediction: {e}")
            return "Explanation unavailable. Please consult your healthcare provider."
    
    def log_interaction(
        self,
        interaction_type: str,
        prompt_length: int,
        response_length: int,
        success: bool,
        error: Optional[str] = None
    ):
        """Log Gemini AI interaction for monitoring"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": interaction_type,
            "prompt_length": prompt_length,
            "response_length": response_length,
            "success": success,
            "error": error
        }
        logger.info(f"Gemini interaction: {json.dumps(log_data)}")


# Global instance
_gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
