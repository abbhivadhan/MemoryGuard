"""
Service for cognitive assessment scoring and management.
Requirements: 12.3
"""

from typing import Dict, Any, Optional
import logging
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class AssessmentScoringService:
    """Service for scoring cognitive assessments with AI-powered evaluation."""
    
    def __init__(self):
        self.gemini_service = GeminiService()
    
    async def evaluate_answer(self, question: str, user_answer: str, expected_answer: str, context: str = "") -> bool:
        """
        Use Gemini AI to intelligently evaluate if an answer is correct.
        Handles variations, synonyms, and reasonable interpretations.
        """
        try:
            prompt = f"""You are evaluating a cognitive assessment answer. Determine if the user's answer is correct.

Question: {question}
Expected Answer: {expected_answer}
User's Answer: {user_answer}
{f"Context: {context}" if context else ""}

Consider:
- Synonyms and variations (e.g., "fall" = "autumn")
- Minor spelling errors
- Reasonable interpretations
- Partial credit for close answers

Respond with ONLY "CORRECT" or "INCORRECT" followed by a brief explanation.
Format: CORRECT|explanation or INCORRECT|explanation"""

            response = await self.gemini_service.generate_content(prompt)
            
            if not response:
                logger.warning(f"No response from Gemini for answer evaluation")
                return False
            
            # Parse response
            parts = response.split("|", 1)
            result = parts[0].strip().upper()
            
            return result == "CORRECT"
            
        except Exception as e:
            logger.error(f"Error evaluating answer with Gemini: {e}")
            # Fallback to simple string matching
            return user_answer.lower().strip() == expected_answer.lower().strip()
    
    def score_mmse(self, responses: Dict[str, Any]) -> int:
        """
        Score MMSE (Mini-Mental State Examination) test.
        Total: 30 points
        
        Requirements: 12.3
        """
        score = 0
        
        # Orientation (10 points)
        # Time orientation (5 points)
        if responses.get("orientation_year") == "correct":
            score += 1
        if responses.get("orientation_season") == "correct":
            score += 1
        if responses.get("orientation_date") == "correct":
            score += 1
        if responses.get("orientation_day") == "correct":
            score += 1
        if responses.get("orientation_month") == "correct":
            score += 1
        
        # Place orientation (5 points)
        if responses.get("orientation_state") == "correct":
            score += 1
        if responses.get("orientation_county") == "correct":
            score += 1
        if responses.get("orientation_town") == "correct":
            score += 1
        if responses.get("orientation_hospital") == "correct":
            score += 1
        if responses.get("orientation_floor") == "correct":
            score += 1
        
        # Registration (3 points)
        if responses.get("registration_word1") == "correct":
            score += 1
        if responses.get("registration_word2") == "correct":
            score += 1
        if responses.get("registration_word3") == "correct":
            score += 1
        
        # Attention and Calculation (5 points)
        # Serial 7s or spelling WORLD backwards
        attention_score = responses.get("attention_score", 0)
        score += min(int(attention_score), 5)
        
        # Recall (3 points)
        if responses.get("recall_word1") == "correct":
            score += 1
        if responses.get("recall_word2") == "correct":
            score += 1
        if responses.get("recall_word3") == "correct":
            score += 1
        
        # Language (9 points)
        # Naming (2 points)
        if responses.get("naming_object1") == "correct":
            score += 1
        if responses.get("naming_object2") == "correct":
            score += 1
        
        # Repetition (1 point)
        if responses.get("repetition") == "correct":
            score += 1
        
        # Three-stage command (3 points)
        if responses.get("command_step1") == "correct":
            score += 1
        if responses.get("command_step2") == "correct":
            score += 1
        if responses.get("command_step3") == "correct":
            score += 1
        
        # Reading (1 point)
        if responses.get("reading") == "correct":
            score += 1
        
        # Writing (1 point)
        if responses.get("writing") == "correct":
            score += 1
        
        # Drawing (1 point)
        if responses.get("drawing") == "correct":
            score += 1
        
        return score
    
    def score_moca(self, responses: Dict[str, Any]) -> int:
        """
        Score MoCA (Montreal Cognitive Assessment) test.
        Total: 30 points
        
        Requirements: 12.3
        """
        score = 0
        
        # Visuospatial/Executive (5 points)
        # Trail making (1 point)
        if responses.get("trail_making") == "correct":
            score += 1
        
        # Cube copy (1 point)
        if responses.get("cube_copy") == "correct":
            score += 1
        
        # Clock drawing (3 points)
        clock_score = responses.get("clock_drawing_score", 0)
        score += min(int(clock_score), 3)
        
        # Naming (3 points)
        if responses.get("naming_lion") == "correct":
            score += 1
        if responses.get("naming_rhino") == "correct":
            score += 1
        if responses.get("naming_camel") == "correct":
            score += 1
        
        # Memory - Registration (0 points, but needed for recall)
        # No points awarded here
        
        # Attention (6 points)
        # Digit span forward (1 point)
        if responses.get("digit_span_forward") == "correct":
            score += 1
        
        # Digit span backward (1 point)
        if responses.get("digit_span_backward") == "correct":
            score += 1
        
        # Vigilance (1 point)
        if responses.get("vigilance") == "correct":
            score += 1
        
        # Serial 7s (3 points)
        serial7_score = responses.get("serial7_score", 0)
        score += min(int(serial7_score), 3)
        
        # Language (3 points)
        # Sentence repetition (2 points)
        if responses.get("sentence_repetition1") == "correct":
            score += 1
        if responses.get("sentence_repetition2") == "correct":
            score += 1
        
        # Fluency (1 point)
        if responses.get("fluency") == "correct":
            score += 1
        
        # Abstraction (2 points)
        if responses.get("abstraction1") == "correct":
            score += 1
        if responses.get("abstraction2") == "correct":
            score += 1
        
        # Delayed Recall (5 points)
        if responses.get("recall_word1") == "correct":
            score += 1
        if responses.get("recall_word2") == "correct":
            score += 1
        if responses.get("recall_word3") == "correct":
            score += 1
        if responses.get("recall_word4") == "correct":
            score += 1
        if responses.get("recall_word5") == "correct":
            score += 1
        
        # Orientation (6 points)
        if responses.get("orientation_date") == "correct":
            score += 1
        if responses.get("orientation_month") == "correct":
            score += 1
        if responses.get("orientation_year") == "correct":
            score += 1
        if responses.get("orientation_day") == "correct":
            score += 1
        if responses.get("orientation_place") == "correct":
            score += 1
        if responses.get("orientation_city") == "correct":
            score += 1
        
        # Education adjustment (1 point if ≤12 years education)
        if responses.get("education_years", 13) <= 12:
            score += 1
        
        return min(score, 30)  # Cap at 30
    
    def get_max_score(self, assessment_type: str) -> int:
        """Get maximum score for assessment type."""
        max_scores = {
            "MMSE": 30,
            "MoCA": 30,
            "CDR": 3,
            "ClockDrawing": 10
        }
        return max_scores.get(assessment_type, 0)
    
    def score_assessment(self, assessment_type: str, responses: Dict[str, Any]) -> Optional[int]:
        """
        Score an assessment based on its type.
        
        Requirements: 12.3
        """
        if assessment_type == "MMSE":
            return self.score_mmse(responses)
        elif assessment_type == "MoCA" or assessment_type == "MOCA":
            return self.score_moca(responses)
        elif assessment_type == "CDR":
            # CDR scoring is more complex and typically done by clinicians
            # Return the score if provided in responses
            return responses.get("cdr_score")
        elif assessment_type == "ClockDrawing" or assessment_type == "CLOCK_DRAWING":
            # Clock drawing typically scored 0-10
            return responses.get("clock_score")
        
        return None
