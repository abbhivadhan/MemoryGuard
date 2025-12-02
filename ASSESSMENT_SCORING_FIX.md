# Assessment Scoring and Display Fix

## Issues Fixed

### 1. Scoring Returns 0/30 Despite Answering All Questions

**Problem**: The frontend was storing responses with actual answer values, but the backend scoring service expected responses with `"correct"` or `"incorrect"` values.

**Solution**:
- Updated `MMSETestNew.tsx` to store responses in the format the backend expects:
  - Main response key (e.g., `orientation_year`) = `"correct"` or `"incorrect"`
  - Answer key (e.g., `orientation_year_answer`) = actual user answer
  - Score key (e.g., `orientation_year_score`) = calculated score

- Updated `assessment_service.py` to handle both new and legacy response formats:
  - Added support for new question IDs (`naming_pencil`, `naming_watch`, `reading_command`, `writing_sentence`, `copying_design`)
  - Added special handling for `three_stage_command_score` which can be 0-3 points
  - Maintained backward compatibility with old format

### 2. Pictures Not Displayed in Assessment

**Problem**: No images were being shown for questions that require visual stimuli (naming objects, copying designs).

**Solution**:
- Added `imageUrl` and `imageAlt` fields to the Question interface
- Added image URLs for relevant questions:
  - Naming pencil: Shows a pencil image
  - Naming watch: Shows a wristwatch image
  - Copying design: Shows intersecting pentagons
- Added image display component in the UI that:
  - Centers the image
  - Applies proper styling (rounded corners, border, shadow)
  - Handles image load errors gracefully
  - Displays between question text and input area

## Changes Made

### Frontend (`frontend/src/components/cognitive/MMSETestNew.tsx`)

1. **Response Format Update**:
```typescript
const newResponses = {
  ...responses,
  [currentQuestion.id]: isCorrect || score > 0 ? "correct" : "incorrect",
  [`${currentQuestion.id}_answer`]: userInput,
  [`${currentQuestion.id}_score`]: score
};
```

2. **Image Support**:
```typescript
interface Question {
  // ... existing fields
  imageUrl?: string;
  imageAlt?: string;
}
```

3. **Image Display**:
```tsx
{currentQuestion.imageUrl && (
  <div className="flex justify-center mb-6">
    <img 
      src={currentQuestion.imageUrl} 
      alt={currentQuestion.imageAlt || 'Assessment image'}
      className="max-w-md w-full rounded-lg border-2 border-white/20 shadow-lg"
      onError={(e) => {
        e.currentTarget.style.display = 'none';
      }}
    />
  </div>
)}
```

### Backend (`backend/app/services/assessment_service.py`)

1. **Updated Question ID Mapping**:
- `naming_pencil` / `naming_object1` → 1 point
- `naming_watch` / `naming_object2` → 1 point
- `reading_command` / `reading` → 1 point
- `writing_sentence` / `writing` → 1 point
- `copying_design` / `drawing` → 1 point

2. **Special Scoring for Three-Stage Command**:
```python
if "three_stage_command_score" in responses:
    score += min(int(responses.get("three_stage_command_score", 0)), 3)
```

## Testing

To verify the fixes:

1. **Scoring Test**:
   - Take an MMSE assessment
   - Answer all questions
   - Verify the final score is calculated correctly (not 0/30)
   - Check that partial credit is given for three-stage command

2. **Image Display Test**:
   - Navigate to naming questions (pencil, watch)
   - Verify images are displayed
   - Navigate to copying design question
   - Verify pentagon image is displayed

## Notes

- Images are loaded from Wikimedia Commons (public domain)
- Image loading errors are handled gracefully (image hides if fails to load)
- Backward compatibility maintained for existing assessments
- AI evaluation still works for text-based answers
