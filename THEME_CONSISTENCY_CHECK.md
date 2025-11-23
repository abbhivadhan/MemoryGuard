# Theme Consistency Check

## Pages Status

### ✅ Already Following Theme Perfectly
1. **DashboardPage** - Black + 3D starfield, glass morphism
2. **MedicationsPage** - Black + 3D starfield, glass morphism, back button
3. **FaceRecognitionPage** - Black + 3D starfield, glass morphism, back button
4. **MemoryAssistantPage** - Black + 3D starfield, glass morphism, back button
5. **CaregiversPage** - Black + 3D starfield, glass morphism, back button
6. **CommunityPage** - Black + 3D starfield, glass morphism, back button

### ⚠️ Need Minor Updates (Dark but no 3D background)
7. **TrainingPage** - Has dark gradient, needs 3D starfield + back button
8. **AssessmentPage** - Has dark gradient, needs 3D starfield + back button
9. **ImagingPage** - Has dark gradient, needs 3D starfield + back button
10. **RecommendationsPage** - Has bg-gray-900, needs 3D starfield + back button
11. **EmergencyPage** - Has bg-gray-900, needs 3D starfield (no back button - emergency)
12. **CaregiverPage** - Has dark theme, needs 3D starfield + back button

### ✅ Special Cases (Correct as-is)
- **HomePage** - Has its own 3D design (landing page)
- **ProviderPortalPage** - Professional portal (different design intentional)

## Required Updates

### Standard Pattern for All Pages:
```tsx
import { Suspense } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, [Icon] } from 'lucide-react';
import Scene from '../components/3d/Scene';
import Starfield from '../components/3d/Starfield';

export default function PageName() {
  const navigate = useNavigate();
  
  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">
      {/* 3D Background Scene */}
      <div className="fixed inset-0 z-0">
        <Scene camera={{ position: [0, 0, 8], fov: 75 }} enablePhysics={false}>
          <Suspense fallback={null}>
            <Starfield count={200} />
          </Suspense>
        </Scene>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Back Button */}
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          onClick={() => navigate('/dashboard')}
          className="mb-6 flex items-center gap-2 text-gray-300 hover:text-white transition-colors backdrop-blur-sm bg-white/5 px-4 py-2 rounded-lg border border-white/10"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Dashboard</span>
        </motion.button>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <motion.div 
              className="p-3 bg-gradient-to-br from-[color1] to-[color2] rounded-2xl"
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ type: 'spring', stiffness: 400 }}
            >
              <Icon className="w-8 h-8 text-white" />
            </motion.div>
            <h1 className="text-4xl md:text-5xl font-bold text-blue-50">
              Page Title
            </h1>
          </div>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Description
          </p>
        </motion.div>

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6"
        >
          {/* Page content here */}
        </motion.div>
      </div>
    </div>
  );
}
```

## Color Gradients by Page

| Page | Gradient | Icon |
|------|----------|------|
| Dashboard | Various | Various |
| Medications | Teal → Cyan | Pill |
| Face Recognition | Pink → Rose | Users |
| Memory Assistant | Blue → Indigo | Calendar |
| Caregivers | Violet → Purple | Users |
| Community | Blue → Indigo | Users |
| Training | Purple → Violet | Dumbbell |
| Assessment | Green → Emerald | Activity |
| Imaging | Indigo → Purple | Camera |
| Recommendations | Yellow → Orange | BookOpen |
| Emergency | Red → Orange | AlertCircle |
| Caregiver Portal | Purple → Indigo | Users |

## Implementation Priority

1. **High Priority** (User-facing pages):
   - TrainingPage
   - AssessmentPage
   - RecommendationsPage

2. **Medium Priority**:
   - ImagingPage
   - CaregiverPage

3. **Low Priority** (Already functional):
   - EmergencyPage (emergency context, less critical)

## Notes

- All pages should have the same 3D starfield background
- All pages should have consistent back button (except emergency)
- All pages should use glass morphism for content containers
- All pages should have animated headers with gradient icons
- Text should be light colors (text-blue-50, text-gray-300, text-gray-400)
- Buttons should use gradient backgrounds with motion effects
