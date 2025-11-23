import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Suspense, lazy } from 'react';
import ProtectedRoute from './components/auth/ProtectedRoute';
import EmergencySystem from './components/emergency/EmergencySystem';
import OfflineIndicator from './components/OfflineIndicator';
import { useAuthStore } from './store/authStore';

// Lazy load pages
const HomePage = lazy(() => import('./pages/HomePage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const EmergencyPage = lazy(() => import('./pages/EmergencyPage'));
const CaregiverPage = lazy(() => import('./pages/CaregiverPage'));
const TrainingPage = lazy(() => import('./pages/TrainingPage'));
const RecommendationsPage = lazy(() => import('./pages/RecommendationsPage'));
const CommunityPage = lazy(() => import('./pages/CommunityPage'));
const PostDetail = lazy(() => import('./components/community/PostDetail'));
const ImagingPage = lazy(() => import('./pages/ImagingPage'));
const ProviderPortalPage = lazy(() => import('./pages/ProviderPortalPage'));
const AccessManagement = lazy(() => import('./components/provider/AccessManagement'));
const MemoryAssistantPage = lazy(() => import('./pages/MemoryAssistantPage'));
const MedicationsPage = lazy(() => import('./pages/MedicationsPage'));
const FaceRecognitionPage = lazy(() => import('./pages/FaceRecognitionPage'));
const AssessmentPage = lazy(() => import('./pages/AssessmentPage'));
const CaregiversPage = lazy(() => import('./pages/CaregiversPage'));

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function EmergencyWrapper() {
  const location = useLocation();
  const { isAuthenticated } = useAuthStore();
  
  // Show emergency button on all pages except home and emergency page
  const showEmergency = isAuthenticated && location.pathname !== '/' && location.pathname !== '/emergency';
  
  return showEmergency ? <EmergencySystem /> : null;
}

function AppContent() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    }>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <DashboardPage />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/emergency"
          element={
            <ProtectedRoute>
              <EmergencyPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/caregiver"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <CaregiverPage />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/caregiver/patient/:patientId"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <CaregiverPage />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/training"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <TrainingPage />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/recommendations"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <RecommendationsPage />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/community"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <CommunityPage />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/community/posts/:postId"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <PostDetail />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/imaging"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <ImagingPage />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/memory-assistant"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <MemoryAssistantPage />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/medications"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <MedicationsPage />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/face-recognition"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <FaceRecognitionPage />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/assessment"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <AssessmentPage />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/caregivers"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <CaregiversPage />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/provider/*"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <ProviderPortalPage />
              </>
            </ProtectedRoute>
          }
        />
        <Route
          path="/access-management"
          element={
            <ProtectedRoute>
              <>
                <EmergencyWrapper />
                <AccessManagement />
              </>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Suspense>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AppContent />
        <OfflineIndicator />
      </Router>
    </QueryClientProvider>
  );
}

export default App;
