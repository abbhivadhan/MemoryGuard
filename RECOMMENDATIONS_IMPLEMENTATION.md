# Personalized Recommendations System Implementation

## Overview

The personalized recommendations system provides evidence-based health recommendations tailored to each user's risk profile and health metrics. The system includes comprehensive tracking, research citations, and interactive 3D tutorials.

**Requirements Implemented:** 15.1, 15.2, 15.3, 15.4, 15.5, 15.6

## Architecture

### Backend Components

#### 1. Database Models (`backend/app/models/recommendation.py`)

**Recommendation Model:**
- Stores personalized health recommendations
- Categories: diet, exercise, sleep, cognitive, social
- Priority levels: low, medium, high, critical
- Research citations with DOI links
- Evidence strength ratings
- Target metrics for tracking improvement
- Adherence scoring

**RecommendationAdherence Model:**
- Tracks daily adherence to recommendations
- Records completion status and notes
- Stores outcome metrics for progress tracking

#### 2. Recommendation Service (`backend/app/services/recommendation_service.py`)

**Key Features:**
- Generates recommendations based on risk factors and current metrics
- Provides category-specific recommendations:
  - **Diet:** Mediterranean diet, omega-3, sugar reduction
  - **Exercise:** Aerobic exercise, strength training
  - **Sleep:** Sleep duration optimization, quality improvement
  - **Cognitive:** Brain training, lifelong learning
  - **Social:** Social engagement, community involvement
- Tracks adherence with 30-day rolling statistics
- Updates recommendations based on progress
- Calculates adherence scores automatically

**Research-Backed Recommendations:**
All recommendations include:
- Scientific citations with DOI links
- Evidence strength ratings (strong/moderate/limited)
- Specific target metrics
- Risk factors that triggered the recommendation

#### 3. API Endpoints (`backend/app/api/v1/recommendations.py`)

```
POST /api/v1/recommendations/generate
  - Generate recommendations from risk factors
  
GET /api/v1/recommendations
  - Get user recommendations (filterable by category)
  
POST /api/v1/recommendations/adherence
  - Track daily adherence
  
GET /api/v1/recommendations/adherence/stats
  - Get adherence statistics
  
POST /api/v1/recommendations/update
  - Update recommendations based on new metrics
```

### Frontend Components

#### 1. Recommendation Service (`frontend/src/services/recommendationService.ts`)

TypeScript service for API communication with full type safety.

#### 2. RecommendationsDashboard (`frontend/src/components/recommendations/RecommendationsDashboard.tsx`)

**Features:**
- Displays all active recommendations
- Category filtering (all, diet, exercise, sleep, cognitive, social)
- Adherence statistics dashboard
- Integration with 3D tutorial system

**Statistics Displayed:**
- Overall adherence rate (last 30 days)
- Total activities tracked
- Completed activities count
- Active categories count
- Per-category adherence rates

#### 3. RecommendationCard (`frontend/src/components/recommendations/RecommendationCard.tsx`)

**Features:**
- Displays recommendation details
- Shows priority and evidence strength
- Expandable research citations
- Target metrics display
- Quick adherence tracking buttons
- Tutorial launch button

#### 4. RecommendationTutorial3D (`frontend/src/components/recommendations/RecommendationTutorial3D.tsx`)

**Interactive 3D Tutorials:**

**Exercise Tutorial:**
- Animated 3D figure demonstrating walking/running
- Shows proper form and movement

**Sleep/Meditation Tutorial:**
- Breathing animation with expanding aura
- Demonstrates relaxation techniques

**Diet Tutorial:**
- 3D visualization of Mediterranean diet components
- Color-coded food groups

**Cognitive Tutorial:**
- Rotating geometric shapes
- Represents brain training activities

**Social Tutorial:**
- Connected spheres representing social networks
- Shows importance of connections

**Tutorial Features:**
- Step-by-step progression
- Progress indicators
- Interactive 3D controls (orbit, zoom)
- Clear descriptions for each step

## Database Migration

**Migration:** `backend/alembic/versions/006_create_recommendation_tables.py`

Creates:
- `recommendations` table with all fields and indexes
- `recommendation_adherence` table for tracking
- Enum types for categories and priorities
- Composite indexes for performance

## Example Recommendations

### Diet Recommendations

1. **Mediterranean Diet** (High Priority)
   - Triggered by: cardiovascular risk > 0.3
   - Evidence: Strong (Scarmeas et al., 2006)
   - Target: cholesterol, blood pressure, inflammation

2. **Omega-3 Fatty Acids** (Medium Priority)
   - Triggered by: cognitive decline > 0.2
   - Evidence: Moderate (Yurko-Mauro et al., 2010)
   - Target: cognitive score, memory function

3. **Reduce Sugar** (High Priority)
   - Triggered by: glucose > 100 or diabetes risk > 0.3
   - Evidence: Strong (Biessels et al., 2014)
   - Target: glucose, insulin sensitivity

### Exercise Recommendations

1. **Aerobic Exercise** (High Priority)
   - Triggered by: physical activity < 150 min/week
   - Evidence: Strong (Hamer & Chida, 2009)
   - Target: cardiovascular fitness, hippocampal volume

2. **Strength Training** (Medium Priority)
   - Evidence: Moderate (Liu-Ambrose et al., 2010)
   - Target: muscle strength, cognitive score

### Sleep Recommendations

1. **Optimize Sleep Duration** (High Priority)
   - Triggered by: sleep < 7 or > 9 hours
   - Evidence: Strong (Ju et al., 2013)
   - Target: sleep hours, amyloid-beta levels

2. **Improve Sleep Quality** (Medium Priority)
   - Triggered by: sleep quality < 7
   - Evidence: Moderate (Osorio et al., 2015)
   - Target: sleep quality, cognitive score

## Usage Flow

### 1. Generate Recommendations

After ML prediction:
```python
service = RecommendationService(db)
recommendations = service.generate_recommendations(
    user_id=user_id,
    risk_factors=prediction.feature_importance,
    current_metrics=latest_health_metrics
)
```

### 2. Track Adherence

User marks recommendation as completed:
```python
adherence = service.track_adherence(
    recommendation_id=rec_id,
    user_id=user_id,
    completed=True,
    notes="Walked 30 minutes"
)
```

### 3. View Statistics

Get adherence stats:
```python
stats = service.get_adherence_stats(user_id, days=30)
# Returns overall rate and per-category breakdown
```

### 4. Update Recommendations

When metrics improve:
```python
updated_recs = service.update_recommendations_based_on_progress(
    user_id=user_id,
    new_metrics=updated_health_metrics
)
```

## Frontend Integration

### Add to Navigation

```typescript
<Link to="/recommendations">
  Recommendations
</Link>
```

### Use in Dashboard

```typescript
import RecommendationsDashboard from './components/recommendations/RecommendationsDashboard';

<RecommendationsDashboard />
```

### Launch Tutorial

```typescript
<RecommendationTutorial3D
  category="exercise"
  onComplete={() => console.log('Tutorial completed')}
/>
```

## Research Citations

All recommendations include peer-reviewed research:

- **Mediterranean Diet:** Scarmeas et al., Annals of Neurology, 2006
- **Omega-3:** Yurko-Mauro et al., Alzheimer's & Dementia, 2010
- **Exercise:** Hamer & Chida, Psychological Medicine, 2009
- **Sleep:** Ju et al., JAMA Neurology, 2013
- **Cognitive Training:** Rebok et al., JAGS, 2014
- **Social Engagement:** Fratiglioni et al., Lancet Neurology, 2004

## Testing

### Backend Tests

```bash
# Test recommendation generation
pytest backend/tests/test_recommendation_service.py

# Test API endpoints
pytest backend/tests/test_recommendations_api.py
```

### Frontend Tests

```bash
# Test components
npm test -- RecommendationsDashboard
npm test -- RecommendationCard
npm test -- RecommendationTutorial3D
```

## Performance Considerations

- Recommendations are cached per user
- Adherence scores calculated on-demand
- Old recommendations deactivated automatically
- Indexes on user_id, category, and date fields
- Lazy loading of research citations

## Future Enhancements

1. **AI-Powered Personalization:**
   - Use Gemini AI for more nuanced recommendations
   - Natural language explanations

2. **Gamification:**
   - Streaks and achievements
   - Leaderboards for adherence

3. **Integration:**
   - Sync with wearable devices
   - Calendar integration for scheduling

4. **Advanced Analytics:**
   - Correlation between adherence and outcomes
   - Predictive adherence modeling

## Conclusion

The personalized recommendations system provides evidence-based, actionable guidance tailored to each user's unique risk profile. With comprehensive tracking, research citations, and interactive 3D tutorials, it empowers users to take control of their brain health through lifestyle modifications.
