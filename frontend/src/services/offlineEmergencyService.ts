/**
 * Offline Emergency Service
 * Provides emergency features that work without internet connectivity
 */

import { offlineStorage, STORES } from './offlineStorage';

export interface EmergencyContact {
  id: string;
  name: string;
  phone: string;
  relationship: string;
  isPrimary: boolean;
}

export interface EmergencyAlert {
  id: string;
  userId: string;
  timestamp: string;
  location?: {
    latitude: number;
    longitude: number;
    accuracy: number;
  };
  type: 'manual' | 'automatic';
  status: 'pending' | 'sent' | 'failed';
  contacts: string[]; // Contact IDs
}

class OfflineEmergencyService {
  /**
   * Trigger emergency alert offline
   */
  async triggerEmergencyAlert(userId: string): Promise<EmergencyAlert> {
    // Get current location
    const location = await this.getCurrentLocation();

    // Create alert
    const alert: EmergencyAlert = {
      id: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      userId,
      timestamp: new Date().toISOString(),
      location,
      type: 'manual',
      status: 'pending',
      contacts: [],
    };

    // Get emergency contacts from cache
    const userData = await offlineStorage.getCachedUserData(userId);
    const contacts: EmergencyContact[] = userData?.emergencyContacts || [];

    if (contacts.length > 0) {
      alert.contacts = contacts.map(c => c.id);

      // Try to send SMS/call using device capabilities
      await this.notifyContactsOffline(contacts, location);
      alert.status = 'sent';
    }

    // Store alert for later sync
    await offlineStorage.addToSyncQueue({
      type: 'create',
      store: 'emergency_alerts',
      data: alert,
    });

    // Show notification
    this.showEmergencyNotification();

    // Vibrate device
    this.vibrateDevice();

    return alert;
  }

  /**
   * Get current location using Geolocation API
   */
  private async getCurrentLocation(): Promise<{ latitude: number; longitude: number; accuracy: number } | undefined> {
    if (!('geolocation' in navigator)) {
      console.warn('Geolocation not supported');
      return undefined;
    }

    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
          });
        },
        (error) => {
          console.error('Error getting location:', error);
          resolve(undefined);
        },
        {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0,
        }
      );
    });
  }

  /**
   * Notify emergency contacts using device capabilities
   */
  private async notifyContactsOffline(contacts: EmergencyContact[], location?: any): Promise<void> {
    const locationText = location
      ? `Location: https://maps.google.com/?q=${location.latitude},${location.longitude}`
      : 'Location unavailable';

    const message = `EMERGENCY ALERT from MemoryGuard! ${locationText}`;

    // Try to use SMS (if available on device)
    for (const contact of contacts) {
      try {
        // Use tel: protocol to initiate call
        if (contact.isPrimary) {
          const telLink = `tel:${contact.phone}`;
          window.open(telLink, '_self');
        }

        // Use sms: protocol to send SMS (on mobile devices)
        const smsLink = `sms:${contact.phone}?body=${encodeURIComponent(message)}`;
        window.open(smsLink, '_blank');
      } catch (error) {
        console.error('Error notifying contact:', error);
      }
    }
  }

  /**
   * Show emergency notification
   */
  private showEmergencyNotification(): void {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Emergency Alert Activated', {
        body: 'Emergency contacts are being notified',
        icon: '/icon-192x192.png',
        badge: '/icon-192x192.png',
        tag: 'emergency',
        requireInteraction: true,
      });
    }
  }

  /**
   * Vibrate device
   */
  private vibrateDevice(): void {
    if ('vibrate' in navigator) {
      // SOS pattern: three short, three long, three short
      navigator.vibrate([200, 100, 200, 100, 200, 300, 500, 100, 500, 100, 500, 300, 200, 100, 200, 100, 200]);
    }
  }

  /**
   * Get safe return home directions (offline)
   */
  async getSafeReturnHome(homeAddress: string): Promise<string> {
    const location = await this.getCurrentLocation();

    if (!location) {
      return 'Unable to get current location. Please ask someone for help.';
    }

    // Generate Google Maps link (will work when device has connectivity)
    const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(homeAddress)}&travelmode=walking`;

    // Try to open maps app
    window.open(mapsUrl, '_blank');

    return mapsUrl;
  }

  /**
   * Store emergency medical information for offline access
   */
  async storeEmergencyMedicalInfo(userId: string, medicalInfo: any): Promise<void> {
    await offlineStorage.put(STORES.USER_DATA, {
      id: `medical-${userId}`,
      userId,
      type: 'emergency_medical_info',
      data: medicalInfo,
      updatedAt: new Date().toISOString(),
    });
  }

  /**
   * Get emergency medical information (works offline)
   */
  async getEmergencyMedicalInfo(userId: string): Promise<any> {
    const data: any = await offlineStorage.get(STORES.USER_DATA, `medical-${userId}`);
    return data?.data;
  }

  /**
   * Cache emergency contacts for offline use
   */
  async cacheEmergencyContacts(userId: string, contacts: EmergencyContact[]): Promise<void> {
    const userData = await offlineStorage.getCachedUserData(userId) || {};
    userData.emergencyContacts = contacts;
    await offlineStorage.cacheUserData(userId, userData);
  }

  /**
   * Get cached emergency contacts
   */
  async getCachedEmergencyContacts(userId: string): Promise<EmergencyContact[]> {
    const userData = await offlineStorage.getCachedUserData(userId);
    return userData?.emergencyContacts || [];
  }

  /**
   * Test emergency system (without actually sending alerts)
   */
  async testEmergencySystem(): Promise<boolean> {
    try {
      // Test location
      const location = await this.getCurrentLocation();
      console.log('Location test:', location ? 'Success' : 'Failed');

      // Test notification
      if ('Notification' in window) {
        const permission = await Notification.requestPermission();
        console.log('Notification permission:', permission);
      }

      // Test vibration
      if ('vibrate' in navigator) {
        navigator.vibrate(200);
        console.log('Vibration test: Success');
      }

      return true;
    } catch (error) {
      console.error('Emergency system test failed:', error);
      return false;
    }
  }
}

// Export singleton instance
export const offlineEmergencyService = new OfflineEmergencyService();
