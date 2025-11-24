import React, { useState } from 'react';
import GoogleAuthButton from './GoogleAuthButton';
import { useAuthStore } from '../../store/authStore';

interface AuthFormProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export default function AuthForm({ onSuccess, onError }: AuthFormProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { loginWithEmail, register } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (!isLogin && password !== confirmPassword) {
        throw new Error('Passwords do not match');
      }

      if (isLogin) {
        // Login
        await loginWithEmail(email, password);
        onSuccess?.();
      } else {
        // Register
        await register(email, password);
        onSuccess?.();
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Authentication failed';
      setError(errorMessage);
      onError?.(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = () => {
    onSuccess?.();
  };

  const handleGoogleError = (error: string) => {
    setError(error);
    onError?.(error);
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl shadow-2xl p-8 hover:border-white/30 transition-all">
        {/* Tab Switcher */}
        <div className="flex mb-6 backdrop-blur-md bg-white/10 rounded-lg p-1 border border-white/20">
          <button
            onClick={() => setIsLogin(true)}
            className={`flex-1 py-2 px-4 rounded-md transition-all font-medium ${
              isLogin
                ? 'bg-blue-600 text-white border border-blue-500'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className={`flex-1 py-2 px-4 rounded-md transition-all font-medium ${
              !isLogin
                ? 'bg-blue-600 text-white border border-blue-500'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            Sign Up
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="backdrop-blur-sm bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-200 mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 backdrop-blur-md bg-white/10 border border-white/20 rounded-lg 
                focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400
                text-white placeholder-gray-400 transition-all hover:border-white/30 hover:bg-white/15"
              placeholder="your@email.com"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-200 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="w-full px-4 py-3 backdrop-blur-md bg-white/10 border border-white/20 rounded-lg 
                focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400
                text-white placeholder-gray-400 transition-all hover:border-white/30 hover:bg-white/15"
              placeholder="••••••••"
            />
          </div>

          {!isLogin && (
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-200 mb-2">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={6}
                className="w-full px-4 py-3 backdrop-blur-md bg-white/10 border border-white/20 rounded-lg 
                  focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400
                  text-white placeholder-gray-400 transition-all hover:border-white/30 hover:bg-white/15"
                placeholder="••••••••"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 
              text-white font-semibold rounded-lg transition-all duration-200 
              transform hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed
              shadow-lg hover:shadow-xl border border-blue-500 disabled:border-gray-500"
          >
            {loading ? 'Please wait...' : isLogin ? 'Login' : 'Sign Up'}
          </button>
        </form>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-white/20"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-4 backdrop-blur-md bg-white/10 text-gray-300">Or</span>
          </div>
        </div>

        {/* Google Auth - Alternative Option */}
        <GoogleAuthButton
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
        />
      </div>
    </div>
  );
}
