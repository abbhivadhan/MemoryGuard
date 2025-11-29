import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { locationService, LocationData } from '../../services/locationService';

interface HomeLocation {
  latitude: number;
  longitude: number;
  address: string;
}

const SafeReturnHome: React.FC = () => {
  const [homeLocation, setHomeLocation] = useState<HomeLocation | null>(null);
  const [, setCurrentLocation] = useState<LocationData | null>(null);
  const [isNavigating, setIsNavigating] = useState(false);
  const [distance, setDistance] = useState<number | null>(null);
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load home location from storage
  useEffect(() => {
    const savedHome = localStorage.getItem('homeLocation');
    if (savedHome) {
      setHomeLocation(JSON.parse(savedHome));
    }
  }, []);

  // Update current location when navigating
  useEffect(() => {
    if (!isNavigating || !homeLocation) return;

    const watchId = locationService.watchLocation(
      (location) => {
        setCurrentLocation(location);
        
        // Calculate distance to home
        const dist = locationService.calculateDistance(
          location.latitude,
          location.longitude,
          homeLocation.latitude,
          homeLocation.longitude
        );
        setDistance(dist);
      },
      (error) => {
        console.error('Location error:', error);
        setError(error.message);
      }
    );

    return () => {
      locationService.clearWatch(watchId);
    };
  }, [isNavigating, homeLocation]);

  const handleSetHomeLocation = async () => {
    setIsLoadingLocation(true);
    setError(null);

    try {
      const location = await locationService.getCurrentLocation();
      const address = await locationService.getAddressFromLocation(location);

      const home: HomeLocation = {
        latitude: location.latitude,
        longitude: location.longitude,
        address,
      };

      setHomeLocation(home);
      localStorage.setItem('homeLocation', JSON.stringify(home));
    } catch (err: any) {
      setError(err.message || 'Failed to get current location');
    } finally {
      setIsLoadingLocation(false);
    }
  };

  const handleStartNavigation = async () => {
    if (!homeLocation) {
      setError('Please set your home location first');
      return;
    }

    setIsNavigating(true);
    setError(null);

    try {
      const location = await locationService.getCurrentLocation();
      setCurrentLocation(location);

      // Open Google Maps with directions
      const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${homeLocation.latitude},${homeLocation.longitude}&travelmode=walking`;
      window.open(mapsUrl, '_blank');
    } catch (err: any) {
      setError(err.message || 'Failed to start navigation');
      setIsNavigating(false);
    }
  };

  const handleStopNavigation = () => {
    setIsNavigating(false);
    setCurrentLocation(null);
    setDistance(null);
  };

  const formatDistance = (meters: number): string => {
    if (meters < 1000) {
      return `${Math.round(meters)}m`;
    }
    return `${(meters / 1000).toFixed(1)}km`;
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center gap-3 mb-4">
        <svg
          className="h-8 w-8 text-green-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
          />
        </svg>
        <h3 className="text-xl font-bold text-white">Safe Return Home</h3>
      </div>

      <p className="text-gray-400 text-sm mb-6">
        Get GPS navigation to help you return home safely if you become disoriented.
      </p>

      {/* Home Location Display */}
      {homeLocation ? (
        <div className="bg-gray-900 rounded-lg p-4 mb-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="text-white font-semibold mb-1">Home Location</h4>
              <p className="text-gray-400 text-sm">{homeLocation.address}</p>
              <p className="text-gray-500 text-xs mt-1">
                {homeLocation.latitude.toFixed(6)}, {homeLocation.longitude.toFixed(6)}
              </p>
            </div>
            <button
              onClick={handleSetHomeLocation}
              disabled={isLoadingLocation}
              className="text-cyan-400 hover:text-cyan-300 text-sm underline"
            >
              Update
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-yellow-900 bg-opacity-30 border border-yellow-700 rounded-lg p-4 mb-6">
          <p className="text-yellow-200 text-sm">
            No home location set. Please set your home location to use this feature.
          </p>
        </div>
      )}

      {/* Navigation Status */}
      <AnimatePresence>
        {isNavigating && distance !== null && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-green-900 bg-opacity-30 border border-green-700 rounded-lg p-4 mb-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-green-300 font-semibold mb-1">Navigating Home</h4>
                <p className="text-green-200 text-sm">
                  Distance: {formatDistance(distance)}
                </p>
              </div>
              <div className="animate-pulse">
                <svg
                  className="h-8 w-8 text-green-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Message */}
      {error && (
        <div className="bg-red-900 bg-opacity-30 border border-red-700 rounded-lg p-4 mb-6">
          <p className="text-red-200 text-sm">{error}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="space-y-3">
        {!homeLocation ? (
          <button
            onClick={handleSetHomeLocation}
            disabled={isLoadingLocation}
            className="w-full px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoadingLocation ? 'Getting Location...' : 'Set Home Location'}
          </button>
        ) : !isNavigating ? (
          <button
            onClick={handleStartNavigation}
            className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
              />
            </svg>
            Navigate Home
          </button>
        ) : (
          <button
            onClick={handleStopNavigation}
            className="w-full px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg transition-colors"
          >
            Stop Navigation
          </button>
        )}
      </div>

      {/* Info Box */}
      <div className="mt-6 bg-blue-900 bg-opacity-30 border border-blue-700 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <svg
            className="h-5 w-5 text-blue-400 flex-shrink-0 mt-0.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <h4 className="text-blue-300 font-semibold text-sm mb-1">How It Works</h4>
            <p className="text-blue-200 text-xs">
              This feature uses GPS to guide you home. When you start navigation, it will
              open Google Maps with walking directions to your home address. Make sure
              location services are enabled on your device.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SafeReturnHome;
