import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../../store/authStore';

interface GoogleAuthButtonProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: any) => void;
          renderButton: (element: HTMLElement, config: any) => void;
          prompt: () => void;
        };
      };
    };
  }
}

const GoogleAuthButton: React.FC<GoogleAuthButtonProps> = ({ onSuccess, onError }) => {
  const { login, isLoading, error } = useAuthStore();
  const [isGoogleLoaded, setIsGoogleLoaded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [isPressed, setIsPressed] = useState(false);
  const buttonRef = React.useRef<HTMLDivElement>(null);

  const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  useEffect(() => {
    // Load Google Identity Services script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = () => {
      setIsGoogleLoaded(true);
    };
    document.body.appendChild(script);

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, []);

  useEffect(() => {
    if (isGoogleLoaded && window.google && buttonRef.current && GOOGLE_CLIENT_ID) {
      // Initialize Google Identity Services
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleResponse,
      });

      // Render the hidden Google button
      window.google.accounts.id.renderButton(
        buttonRef.current,
        {
          theme: 'filled_blue',
          size: 'large',
          text: 'signin_with',
          shape: 'rectangular',
          width: 280,
        }
      );
    }
  }, [isGoogleLoaded, GOOGLE_CLIENT_ID]);

  const handleGoogleResponse = async (response: any) => {
    try {
      const googleToken = response.credential;
      await login(googleToken);
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Authentication failed';
      console.error('Google authentication error:', errorMessage);
      
      if (onError) {
        onError(errorMessage);
      }
    }
  };

  const handleClick = () => {
    if (isLoading || !isGoogleLoaded || !buttonRef.current) return;
    
    // Click the hidden Google button
    const googleButton = buttonRef.current.querySelector('div[role="button"]') as HTMLElement;
    if (googleButton) {
      googleButton.click();
    }
  };

  if (!GOOGLE_CLIENT_ID) {
    return (
      <div className="text-red-500 text-sm">
        Google Client ID not configured. Please set VITE_GOOGLE_CLIENT_ID in your environment.
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Hidden Google button */}
      <div ref={buttonRef} className="hidden" />

      {/* Custom styled button */}
      <button
        onClick={handleClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onMouseDown={() => setIsPressed(true)}
        onMouseUp={() => setIsPressed(false)}
        disabled={isLoading || !isGoogleLoaded}
        className={`
          group relative w-full max-w-sm
          flex items-center justify-center gap-3
          px-6 py-4
          bg-white/95 hover:bg-white
          border-2 border-gray-200/50
          rounded-2xl
          font-medium text-gray-700
          transition-all duration-300 ease-out
          overflow-hidden
          ${isPressed ? 'scale-[0.98]' : isHovered ? 'scale-[1.02]' : 'scale-100'}
          ${isLoading ? 'opacity-70 cursor-not-allowed' : 'cursor-pointer hover:shadow-2xl hover:shadow-blue-500/20'}
          disabled:opacity-50 disabled:cursor-not-allowed
        `}
        style={{
          boxShadow: isHovered 
            ? '0 20px 60px -15px rgba(59, 130, 246, 0.3), 0 0 0 1px rgba(59, 130, 246, 0.1)' 
            : '0 10px 30px -10px rgba(0, 0, 0, 0.1)',
        }}
      >
        {/* Animated gradient background */}
        <div 
          className={`
            absolute inset-0 
            bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-pink-500/5
            transition-opacity duration-500
            ${isHovered ? 'opacity-100' : 'opacity-0'}
          `}
        />
        
        {/* Shimmer effect */}
        <div 
          className={`
            absolute inset-0 
            bg-gradient-to-r from-transparent via-white/40 to-transparent
            transform -skew-x-12
            transition-transform duration-1000
            ${isHovered ? 'translate-x-full' : '-translate-x-full'}
          `}
        />

        {/* Google Logo */}
        <div className={`
          relative z-10
          transition-transform duration-300
          ${isHovered ? 'rotate-[360deg] scale-110' : 'rotate-0 scale-100'}
        `}>
          {isLoading ? (
            <div className="w-6 h-6 border-3 border-blue-500 border-t-transparent rounded-full animate-spin" />
          ) : (
            <svg className="w-6 h-6" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
          )}
        </div>

        {/* Button Text */}
        <span className={`
          relative z-10
          text-base font-semibold
          bg-gradient-to-r from-gray-700 to-gray-900
          bg-clip-text
          transition-all duration-300
          ${isHovered ? 'tracking-wide' : 'tracking-normal'}
        `}>
          {isLoading ? 'Signing in...' : 'Continue with Google'}
        </span>

        {/* Pulse effect on hover */}
        {isHovered && !isLoading && (
          <div className="absolute inset-0 rounded-2xl animate-ping opacity-20 bg-blue-400" 
               style={{ animationDuration: '2s' }} 
          />
        )}
      </button>

      {/* Loading indicator */}
      {isLoading && (
        <div className="text-sm text-gray-400">
          Authenticating...
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="text-sm text-red-500 max-w-xs text-center">
          {error}
        </div>
      )}
    </div>
  );
};

export default GoogleAuthButton;
