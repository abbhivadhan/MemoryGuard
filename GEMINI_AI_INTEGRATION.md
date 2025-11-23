# Google Gemini AI Integration

## Overview

The MemoryGuard application now integrates Google's Gemini AI API to provide intelligent health insights, conversational assistance, cognitive assessment analysis, and ML prediction explanations.

## Features Implemented

### 1. Health Insights Generation
- Analyzes user health data to provide personalized recommendations
- Focuses on cognitive health and Alzheimer's risk reduction
- Evidence-based insights with scientific rationale
- Actionable next steps

### 2. Conversational Health Assistant
- Context-aware chat interface
- Empathetic responses for patients and caregivers
- Maintains conversation history
- Simple, clear language optimized for cognitive accessibility

### 3. Cognitive Assessment Analysis
- Detailed feedback on MMSE, MoCA, and other assessments
- Identifies strengths and areas for improvement
- Personalized suggestions for cognitive enhancement

### 4. ML Prediction Explanations
- Translates technical ML outputs to plain language
- Helps users understand risk assessments
- Context-specific explanations

## Configuration

### Backend Setup

1. **Get Gemini API Key**
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy the key

2. **Configure Environment Variables**
   
   Add to `backend/.env`:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-pro
   GEMINI_MAX_TOKENS=2048
   GEMINI_TEMPERATURE=0.7
   GEMINI_RATE_LIMIT_PER_MINUTE=60
   GEMINI_TIMEOUT_SECONDS=30
   GEMINI_MAX_RETRIES=3
   ```

3. **Install Dependencies**
   ```bash
   cd backend
   pip install google-generativeai tenacity
   ```

## API Endpoints

### POST /api/v1/gemini/health-insights
Generate personalized health insights.

**Request:**
```json
{
  "user_data": {
    "cognitive_scores": {...},
    "biomarkers": {...},
    "lifestyle": {...}
  },
  "focus_areas": ["diet", "exercise", "sleep"]
}
```

**Response:**
```json
{
  "insights": ["..."],
  "recommendations": ["..."],
  "warnings": ["..."],
  "next_steps": ["..."]
}
```

### POST /api/v1/gemini/chat
Conversational health assistant.

**Request:**
```json
{
  "message": "What exercises are good for cognitive health?",
  "conversation_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "user_context": {...}
}
```

**Response:**
```json
{
  "response": "...",
  "conversation_id": "..."
}
```

### POST /api/v1/gemini/analyze-assessment
Analyze cognitive assessment results.

**Request:**
```json
{
  "assessment_type": "MMSE",
  "responses": {...},
  "score": 24,
  "max_score": 30
}
```

**Response:**
```json
{
  "feedback": "...",
  "strengths": ["..."],
  "areas_for_improvement": ["..."],
  "suggestions": ["..."]
}
```

### POST /api/v1/gemini/explain-prediction
Explain ML prediction in plain language.

**Request:**
```json
{
  "prediction_data": {
    "risk_score": 0.65,
    "confidence_interval": [0.55, 0.75],
    "feature_importance": {...}
  },
  "user_friendly": true
}
```

**Response:**
```json
{
  "explanation": "..."
}
```

### GET /api/v1/gemini/status
Check service availability.

**Response:**
```json
{
  "available": true,
  "model": "gemini-pro"
}
```

## Security Features

### Input Sanitization
- Removes email addresses, phone numbers, SSNs, credit card numbers
- Truncates inputs to maximum length
- Validates all user inputs before API calls

### Rate Limiting
- 60 requests per minute per user (configurable)
- Redis-based rate limiting
- Graceful error handling on limit exceeded

### Content Filtering
- Gemini's built-in safety settings enabled
- Blocks harmful, harassing, or inappropriate content
- PII detection and removal

### Error Handling
- Automatic retry with exponential backoff
- Graceful degradation when service unavailable
- Fallback responses for all features

## Caching

- Response caching with Redis
- 1-hour TTL for health insights
- Reduces API costs and improves response times
- Cache keys based on input hash

## Logging

All Gemini AI interactions are logged with:
- Timestamp
- Interaction type
- Prompt and response lengths
- Success/failure status
- Error messages (if any)

Logs are used for:
- Cost management
- Quality monitoring
- Performance optimization
- Debugging

## Frontend Integration

### Using the Gemini Service

```typescript
import geminiService from './services/geminiService';

// Generate health insights
const insights = await geminiService.generateHealthInsights({
  user_data: healthData,
  focus_areas: ['diet', 'exercise']
});

// Chat with assistant
const response = await geminiService.chat({
  message: 'How can I improve my memory?',
  conversation_history: messages
});

// Analyze assessment
const analysis = await geminiService.analyzeAssessment({
  assessment_type: 'MMSE',
  responses: assessmentData,
  score: 24,
  max_score: 30
});

// Explain prediction
const explanation = await geminiService.explainPrediction({
  prediction_data: mlPrediction,
  user_friendly: true
});
```

### Using the Chat Component

```tsx
import HealthAssistantChat from './components/gemini/HealthAssistantChat';

function MyComponent() {
  return (
    <HealthAssistantChat
      userContext={{ age: 65, risk_level: 'moderate' }}
      onClose={() => console.log('Chat closed')}
    />
  );
}
```

## Graceful Degradation

When Gemini AI is unavailable:
- Fallback responses are provided
- Users are informed of limited availability
- Core application functionality continues
- Clear messaging to consult healthcare providers

## Cost Management

- Rate limiting prevents excessive API usage
- Response caching reduces redundant calls
- Configurable token limits
- Usage logging for monitoring

## Best Practices

1. **Always include medical disclaimers**
   - Remind users to consult healthcare professionals
   - Never diagnose or prescribe

2. **Sanitize all inputs**
   - Remove PII before sending to API
   - Validate input lengths and formats

3. **Handle errors gracefully**
   - Provide fallback responses
   - Log errors for debugging
   - Don't expose technical details to users

4. **Monitor usage**
   - Track API calls and costs
   - Monitor response quality
   - Adjust rate limits as needed

5. **Cache when possible**
   - Cache common queries
   - Use appropriate TTLs
   - Invalidate cache when data changes

## Troubleshooting

### "Gemini AI is not configured"
- Check that `GEMINI_API_KEY` is set in `.env`
- Verify API key is valid
- Restart backend service

### "Rate limit exceeded"
- Wait 60 seconds and try again
- Increase `GEMINI_RATE_LIMIT_PER_MINUTE` if needed
- Check Redis connection

### "Service unavailable"
- Check internet connectivity
- Verify Gemini API status
- Check backend logs for errors
- Fallback responses will be used automatically

### Poor response quality
- Adjust `GEMINI_TEMPERATURE` (lower = more focused)
- Modify system instructions in service
- Provide more context in prompts

## Future Enhancements

- Multi-language support
- Voice input/output integration
- Personalized conversation styles
- Integration with wearable devices
- Proactive health recommendations
- Family caregiver coaching

## References

- [Google Gemini AI Documentation](https://ai.google.dev/docs)
- [Gemini API Reference](https://ai.google.dev/api)
- [Safety Settings](https://ai.google.dev/docs/safety_setting_gemini)
