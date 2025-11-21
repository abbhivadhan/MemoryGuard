export interface LocationData {
  latitude: number;
  longitude: number;
  accuracy: number;
  timestamp: number;
  address?: string;
}

export interface LocationError {
  code: number;
  message: string;
}

class LocationService {
  /**
   * Request location permissions from the user
   */
  async requestPermission(): Promise<PermissionState> {
    try {
      if (!navigator.geolocation) {
        throw new Error('Geolocation is not supported by this browser');
      }

      // Check if Permissions API is available
      if (navigator.permissions) {
        const result = await navigator.permissions.query({ name: 'geolocation' });
        return result.state;
      }

      // Fallback: try to get location to trigger permission prompt
      return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
          () => resolve('granted'),
          (error) => {
            if (error.code === error.PERMISSION_DENIED) {
              resolve('denied');
            } else {
              reject(error);
            }
          }
        );
      });
    } catch (error) {
      console.error('Error requesting location permission:', error);
      throw error;
    }
  }

  /**
   * Get current location
   */
  async getCurrentLocation(): Promise<LocationData> {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject({
          code: 0,
          message: 'Geolocation is not supported by this browser',
        });
        return;
      }

      const options = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      };

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const locationData: LocationData = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: position.timestamp,
          };
          resolve(locationData);
        },
        (error) => {
          const locationError: LocationError = {
            code: error.code,
            message: this.getErrorMessage(error.code),
          };
          reject(locationError);
        },
        options
      );
    });
  }

  /**
   * Watch location changes (for navigation features)
   */
  watchLocation(
    onSuccess: (location: LocationData) => void,
    onError: (error: LocationError) => void
  ): number {
    if (!navigator.geolocation) {
      onError({
        code: 0,
        message: 'Geolocation is not supported by this browser',
      });
      return -1;
    }

    const options = {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 5000,
    };

    return navigator.geolocation.watchPosition(
      (position) => {
        const locationData: LocationData = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: position.timestamp,
        };
        onSuccess(locationData);
      },
      (error) => {
        const locationError: LocationError = {
          code: error.code,
          message: this.getErrorMessage(error.code),
        };
        onError(locationError);
      },
      options
    );
  }

  /**
   * Stop watching location
   */
  clearWatch(watchId: number): void {
    if (navigator.geolocation && watchId !== -1) {
      navigator.geolocation.clearWatch(watchId);
    }
  }

  /**
   * Format location for sharing (Google Maps link)
   */
  formatLocationForSharing(location: LocationData): string {
    return `https://www.google.com/maps?q=${location.latitude},${location.longitude}`;
  }

  /**
   * Format location as human-readable string
   */
  formatLocationString(location: LocationData): string {
    return `Lat: ${location.latitude.toFixed(6)}, Lng: ${location.longitude.toFixed(6)} (±${Math.round(location.accuracy)}m)`;
  }

  /**
   * Reverse geocode location to get address (using browser's built-in or external API)
   */
  async getAddressFromLocation(location: LocationData): Promise<string> {
    try {
      // Using OpenStreetMap Nominatim API (free, no API key required)
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${location.latitude}&lon=${location.longitude}&zoom=18&addressdetails=1`,
        {
          headers: {
            'User-Agent': 'MemoryGuard Emergency System',
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch address');
      }

      const data = await response.json();
      return data.display_name || this.formatLocationString(location);
    } catch (error) {
      console.error('Error getting address:', error);
      return this.formatLocationString(location);
    }
  }

  /**
   * Calculate distance between two locations (in meters)
   */
  calculateDistance(
    lat1: number,
    lon1: number,
    lat2: number,
    lon2: number
  ): number {
    const R = 6371e3; // Earth's radius in meters
    const φ1 = (lat1 * Math.PI) / 180;
    const φ2 = (lat2 * Math.PI) / 180;
    const Δφ = ((lat2 - lat1) * Math.PI) / 180;
    const Δλ = ((lon2 - lon1) * Math.PI) / 180;

    const a =
      Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
      Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
  }

  /**
   * Get error message from error code
   */
  private getErrorMessage(code: number): string {
    switch (code) {
      case 1:
        return 'Location permission denied. Please enable location access in your browser settings.';
      case 2:
        return 'Location unavailable. Please check your device settings.';
      case 3:
        return 'Location request timed out. Please try again.';
      default:
        return 'An unknown error occurred while getting your location.';
    }
  }
}

export const locationService = new LocationService();
