import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthForm from '../components/auth/AuthForm';
import { useAuthStore } from '../store/authStore';
import Scene from '../components/3d/Scene';
import ScrollSection from '../components/3d/ScrollSection';
import DynamicScene from '../components/3d/DynamicScene';
import ScrollIndicator from '../components/ScrollIndicator';
import Watermark from '../components/Watermark';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  const [deterioration, setDeterioration] = useState(0);
  const [currentSection, setCurrentSection] = useState(0);

  const handleAuthSuccess = () => {
    // Redirect to dashboard after successful authentication
    navigate('/dashboard');
  };

  const handleAuthError = (error: string) => {
    console.error('Authentication error:', error);
  };

  // If already authenticated, show dashboard link
  if (isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">MemoryGuard</h1>
          <p className="text-xl text-gray-400 mb-8">You are already logged in</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="relative bg-black text-white">
      {/* Fixed 3D Background Scene */}
      <div className="fixed inset-0 z-0">
        <Scene camera={{ position: [0, 0, 8], fov: 75 }} enablePhysics={true}>
          <DynamicScene section={currentSection} deterioration={deterioration} />
        </Scene>
      </div>

      {/* Hero Section */}
      <div className="relative z-10 min-h-screen flex items-center justify-center">
        <div className="w-full max-w-7xl px-6 py-20">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left side - Branding */}
            <div className="space-y-8">
              <div className="space-y-4">
                <h1 className="text-7xl lg:text-8xl font-bold tracking-tight">
                  MemoryGuard
                </h1>
                <div className="h-1 w-24 bg-gradient-to-r from-indigo-500 to-purple-500" />
              </div>
              
              <p className="text-3xl font-light text-gray-300">
                Alzheimer's Early Detection & Support
              </p>
              
              <p className="text-xl text-gray-400 leading-relaxed max-w-xl">
                Combining advanced machine learning for early detection with practical daily assistance features
              </p>

              {/* Scroll Indicator */}
              <div className="pt-8">
                <ScrollIndicator />
              </div>
            </div>

            {/* Right side - Auth Form */}
            <div className="flex justify-center lg:justify-end">
              <AuthForm 
                onSuccess={handleAuthSuccess}
                onError={handleAuthError}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Scroll-triggered sections */}
      <div className="relative z-10">
        <ScrollSection 
          onDeteriorationChange={setDeterioration}
          onSectionChange={setCurrentSection}
        />
      </div>

      {/* Final CTA Section */}
      <div className="relative z-10 min-h-screen flex flex-col">
        <div className="flex-1 flex items-center justify-center">
          <div className="w-full max-w-4xl px-6 text-center space-y-12">
            <div className="space-y-6">
              <h2 className="text-6xl font-bold">
                Ready to Get Started?
              </h2>
              
              <p className="text-2xl text-gray-300 max-w-2xl mx-auto">
                Join MemoryGuard today and take control of your cognitive health
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
              {/* Primary CTA Button */}
              <button
                onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                className="group relative px-10 py-4 overflow-hidden rounded-xl transition-all duration-300 
                  transform hover:scale-105 active:scale-95 backdrop-blur-sm"
              >
                {/* Glass morphism background */}
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 
                  border border-indigo-400/30 rounded-xl" />
                
                {/* Inner glow */}
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-600/40 to-purple-600/40 
                  opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl blur-sm" />
                
                {/* Button content */}
                <span className="relative text-white text-lg font-semibold">
                  Get Started Now
                </span>
              </button>
              
              {/* Secondary Button */}
              <button
                onClick={() => window.scrollTo({ top: window.innerHeight, behavior: 'smooth' })}
                className="group relative px-10 py-4 rounded-xl transition-all duration-300 
                  transform hover:scale-105 active:scale-95 backdrop-blur-sm
                  border border-white/20 hover:border-white/40 bg-white/5 hover:bg-white/10"
              >
                <span className="relative flex items-center gap-3 text-white text-lg font-semibold">
                  Learn More
                  <svg className="w-5 h-5 transform group-hover:translate-x-1 transition-transform" 
                    fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* Watermark at bottom */}
        <Watermark />
      </div>
    </div>
  );
};

export default HomePage;
