# Recommendations System Guide

## Overview

The Recommendations system provides personalized, evidence-based lifestyle interventions to support brain health and reduce Alzheimer's risk. All recommendations are generated from real user data and backed by scientific research.

## Features

### 1. Personalized Recommendations
- Generated based on ML risk predictions and current health metrics
- Five categories: Diet, Exercise, Sleep, Cognitive, Social
- Priority levels: Low, Medium, High, Critical
- Evidence strength ratings: Strong, Moderate, Limited

### 2. Scientific Evidence
- Each recommendation includes peer-reviewed research citations
- DOI links to original studies
- Evidence strength ratings based on research quality

### 3. Adherence Tracking
- Track daily completion of recommendations
- View adherence statistics over time
- Category-specific adherence rates
- Overall adherence percentage

### 4. Interactive Tutorials
- 3D interactive tutorials for each category
- Visual demonstrations of recommended activities
- Step-by-step guidance

## Data Flow

### Recommendation Generation

1. **Input Data**:
   - Risk factors from ML predictions (feature importance)
   - Current health metrics (sleep, activity, glucose, etc.)
   - User health history

2. **Generation Process**:
   - Service analyzes risk factors and metrics
   - Generates category-specific recommendations
   - Assigns priority based on risk levels
   - Includes research citations and evidence

3. **Output**:
   - Active recommendations for the user
   - Target metrics for each recommendation
   - Adherence tracking setup

### Adherence Tracking

1. **User Actions**:
   - Mark recommendation as "Completed Today"
   - Mark as "Skipped Today"
   - Optional notes and outcome metrics

2. **Statistics Calculation**:
   - Overall adherence rate (last 30 days)
   - Category-specific rates
   - Total activities tracked
   - Completed activities count

## API Endpoints

### Generate Recommendations
```
POST /api/v1/recommendations/generate
Body: {
  "risk_factors": { "cognitive_decline": 0.3, ... },
  "current_metrics": { "sleep_hours": 7, ... }
}
```

### Get Recommendations
```
GET /api/v1/recommendations?category=diet&active_only=true
```

### Track Adherence
```
POST /api/v1/recommendations/adherence
Body: {
  "recommendation_id": "uuid",
  "completed": true,
  "notes": "optional",
  "outcome_metrics": {}
}
```

### Get Adherence Stats
```
GET /api/v1/recommendations/adherence/stats?days=30
```

## Usage

### For Users

1. **View Recommendations**:
   - Navigate to Recommendations page from dashboard
   - Filter by category (All, Diet, Exercise, Sleep, Cognitive, Social)
   - View adherence statistics at the top

2. **Track Adherence**:
   - Click "Completed Today" when you follow a recommendation
   - Click "Skipped Today" if you didn't follow it
   - View your adherence score update in real-time

3. **Learn More**:
   - Click "View Research" to see scientific evidence
   - Click "Tutorial" for interactive guidance
   - Read target metrics to understand goals

### For Developers

#### Generate Recommendations for All Users
```bash
cd backend
python scripts/generate_recommendations.py
```

#### Generate for Specific User
```bash
python scripts/generate_recommendations.py <user_id>
```

#### Test Recommendations System
```bash
python test_recommendations.py
```

## Recommendation Categories

### Diet
- Mediterranean diet adoption
- Omega-3 fatty acid intake
- Sugar reduction
- Anti-inflammatory foods
- Hydration

### Exercise
- Aerobic exercise (150 min/week)
- Strength training (2-3x/week)
- Balance exercises
- Flexibility training
- Daily movement

### Sleep
- Sleep duration optimization (7-8 hours)
- Sleep quality improvement
- Sleep apnea screening
- Sleep hygiene practices
- Consistent sleep schedule

### Cognitive
- Cognitive training exercises
- Lifelong learning activities
- Memory exercises
- Problem-solving tasks
- Mental stimulation

### Social
- Social engagement increase
- Community involvement
- Support group participation
- Meaningful relationships
- Volunteer activities

## Evidence Strength Levels

### Strong Evidence
- Multiple large-scale RCTs
- Meta-analyses showing consistent results
- Long-term follow-up studies
- Clear biological mechanisms

### Moderate Evidence
- Some RCTs with positive results
- Observational studies
- Emerging research
- Plausible mechanisms

### Limited Evidence
- Small studies
- Preliminary research
- Theoretical benefits
- Indirect evidence

## Database Schema

### Recommendations Table
- `id`: UUID primary key
- `user_id`: Foreign key to users
- `category`: Enum (diet, exercise, sleep, cognitive, social)
- `priority`: Enum (low, medium, high, critical)
- `title`: String
- `description`: Text
- `research_citations`: JSON array
- `evidence_strength`: String
- `is_active`: Boolean
- `adherence_score`: Float (0-1)
- `generated_from_risk_factors`: JSON
- `target_metrics`: JSON array
- `generated_at`: Timestamp
- `last_updated`: Timestamp

### Recommendation Adherence Table
- `id`: UUID primary key
- `recommendation_id`: Foreign key
- `user_id`: Foreign key
- `date`: Timestamp
- `completed`: Boolean
- `notes`: Text (optional)
- `outcome_metrics`: JSON (optional)

## UI Components

### RecommendationsPage
- Main page container
- 3D starfield background
- Header with navigation
- Dashboard integration

### RecommendationsDashboard
- Adherence statistics cards
- Category filter buttons
- Recommendations grid
- Loading and error states
- Empty state with call-to-action

### RecommendationCard
- Category icon (Lucide icons, no emojis)
- Priority badge
- Evidence strength indicator
- Adherence score display
- Description and target metrics
- Expandable research citations
- Action buttons (Complete/Skip/Tutorial)

## Best Practices

### For Users
1. Review recommendations daily
2. Track adherence consistently
3. Read research citations to understand benefits
4. Use tutorials for proper technique
5. Focus on high-priority items first

### For Developers
1. Generate recommendations after ML predictions
2. Update recommendations when metrics change significantly
3. Ensure all data comes from database (no hardcoded content)
4. Validate user input for adherence tracking
5. Monitor adherence statistics for insights

## Troubleshooting

### No Recommendations Showing
- Ensure user has completed a risk prediction
- Check if recommendations were generated
- Run: `python scripts/generate_recommendations.py <user_id>`

### Adherence Not Updating
- Check database connection
- Verify recommendation_id is valid
- Check user authentication

### Missing Research Citations
- Verify recommendation generation includes citations
- Check JSON structure in database
- Ensure citations array is not empty

## Future Enhancements

1. **Personalization**:
   - Machine learning for recommendation ranking
   - Adaptive recommendations based on adherence
   - Seasonal and contextual recommendations

2. **Social Features**:
   - Share progress with caregivers
   - Community challenges
   - Peer support groups

3. **Integration**:
   - Wearable device data
   - Calendar integration
   - Reminder notifications

4. **Analytics**:
   - Correlation between adherence and outcomes
   - Predictive adherence modeling
   - Personalized intervention timing

## References

All recommendations are based on peer-reviewed research. Key sources include:
- Annals of Neurology
- Alzheimer's & Dementia
- JAMA Neurology
- Lancet Neurology
- Nature Reviews Neuroscience

## Support

For issues or questions:
1. Check this guide
2. Review API documentation
3. Run test scripts
4. Check application logs
5. Contact development team
