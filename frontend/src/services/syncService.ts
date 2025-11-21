/**
 * Data Synchronization Service
 * Handles syncing offline data with the server when connectivity is restored
 */

import { offlineStorage, STORES } from './offlineStorage';
import api from './api';

export interface SyncStatus {
  isSyncing: boolean;
  lastSyncTime: number | null;
  pendingItems: number;
  errors: string[];
}

class SyncService {
  private syncStatus: SyncStatus = {
    isSyncing: false,
    lastSyncTime: null,
    pendingItems: 0,
    errors: [],
  };
  private listeners: Set<(status: SyncStatus) => void> = new Set();
  private syncInterval: number | null = null;

  constructor() {
    this.init();
  }

  /**
   * Initialize sync service
   */
  private init(): void {
    // Listen for online/offline events
    window.addEventListener('online', () => this.handleOnline());
    window.addEventListener('offline', () => this.handleOffline());

    // Start periodic sync check if online
    if (navigator.onLine) {
      this.startPeriodicSync();
    }

    // Initialize offline storage
    offlineStorage.init();
  }

  /**
   * Handle online event
   */
  private async handleOnline(): Promise<void> {
    console.log('Connection restored, starting sync...');
    this.startPeriodicSync();
    await this.syncAll();
  }

  /**
   * Handle offline event
   */
  private handleOffline(): void {
    console.log('Connection lost, stopping sync...');
    this.stopPeriodicSync();
  }

  /**
   * Start periodic sync (every 10 seconds when online)
   */
  private startPeriodicSync(): void {
    if (this.syncInterval) return;

    this.syncInterval = window.setInterval(() => {
      if (navigator.onLine && !this.syncStatus.isSyncing) {
        this.syncAll();
      }
    }, 10000);
  }

  /**
   * Stop periodic sync
   */
  private stopPeriodicSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  /**
   * Sync all pending data
   */
  async syncAll(): Promise<void> {
    if (!navigator.onLine || this.syncStatus.isSyncing) return;

    this.updateStatus({ isSyncing: true, errors: [] });

    try {
      const syncQueue = await offlineStorage.getSyncQueue();
      this.updateStatus({ pendingItems: syncQueue.length });

      if (syncQueue.length === 0) {
        this.updateStatus({ 
          isSyncing: false, 
          lastSyncTime: Date.now(),
          pendingItems: 0 
        });
        return;
      }

      // Group items by store
      const itemsByStore = this.groupByStore(syncQueue);

      // Sync each store
      for (const [store, items] of Object.entries(itemsByStore)) {
        await this.syncStore(store, items);
      }

      // Clear sync queue after successful sync
      await offlineStorage.clearSyncQueue();

      this.updateStatus({ 
        isSyncing: false, 
        lastSyncTime: Date.now(),
        pendingItems: 0 
      });

      console.log('Sync completed successfully');
    } catch (error) {
      console.error('Sync error:', error);
      this.updateStatus({ 
        isSyncing: false,
        errors: [...this.syncStatus.errors, (error as Error).message]
      });
    }
  }

  /**
   * Group sync items by store
   */
  private groupByStore(items: any[]): Record<string, any[]> {
    return items.reduce((acc, item) => {
      if (!acc[item.store]) {
        acc[item.store] = [];
      }
      acc[item.store].push(item);
      return acc;
    }, {} as Record<string, any[]>);
  }

  /**
   * Sync a specific store
   */
  private async syncStore(store: string, items: any[]): Promise<void> {
    const endpoint = this.getEndpointForStore(store);
    if (!endpoint) return;

    for (const item of items) {
      try {
        switch (item.type) {
          case 'create':
            await api.post(endpoint, item.data);
            break;
          case 'update':
            await api.put(`${endpoint}/${item.data.id}`, item.data);
            break;
          case 'delete':
            await api.delete(`${endpoint}/${item.data.id}`);
            break;
        }
      } catch (error) {
        console.error(`Error syncing ${store} item:`, error);
        throw error;
      }
    }
  }

  /**
   * Get API endpoint for store
   */
  private getEndpointForStore(store: string): string | null {
    const endpoints: Record<string, string> = {
      [STORES.REMINDERS]: '/api/v1/reminders',
      [STORES.ROUTINES]: '/api/v1/routines',
      [STORES.MEDICATIONS]: '/api/v1/medications',
      [STORES.HEALTH_METRICS]: '/api/v1/health/metrics',
      [STORES.ASSESSMENTS]: '/api/v1/assessments',
    };

    return endpoints[store] || null;
  }

  /**
   * Cache data for offline use
   */
  async cacheData(userId: string): Promise<void> {
    if (!navigator.onLine) return;

    try {
      // Fetch and cache reminders
      const reminders = await api.get(`/api/v1/reminders/${userId}`);
      for (const reminder of reminders.data) {
        await offlineStorage.put(STORES.REMINDERS, reminder);
      }

      // Fetch and cache routines
      const routines = await api.get(`/api/v1/routines/${userId}`);
      for (const routine of routines.data) {
        await offlineStorage.put(STORES.ROUTINES, routine);
      }

      // Fetch and cache medications
      const medications = await api.get(`/api/v1/medications/${userId}`);
      for (const medication of medications.data) {
        await offlineStorage.put(STORES.MEDICATIONS, medication);
      }

      // Fetch and cache health metrics (last 30 days)
      const healthMetrics = await api.get(`/api/v1/health/metrics/${userId}`);
      for (const metric of healthMetrics.data) {
        await offlineStorage.put(STORES.HEALTH_METRICS, metric);
      }

      // Cache user data
      await offlineStorage.cacheUserData(userId, {
        reminders: reminders.data,
        routines: routines.data,
        medications: medications.data,
        healthMetrics: healthMetrics.data,
      });

      console.log('Data cached successfully for offline use');
    } catch (error) {
      console.error('Error caching data:', error);
    }
  }

  /**
   * Get sync status
   */
  getStatus(): SyncStatus {
    return { ...this.syncStatus };
  }

  /**
   * Subscribe to sync status updates
   */
  subscribe(listener: (status: SyncStatus) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /**
   * Update sync status and notify listeners
   */
  private updateStatus(updates: Partial<SyncStatus>): void {
    this.syncStatus = { ...this.syncStatus, ...updates };
    this.listeners.forEach(listener => listener(this.syncStatus));
  }

  /**
   * Force sync now
   */
  async forceSyncNow(): Promise<void> {
    if (!navigator.onLine) {
      throw new Error('Cannot sync while offline');
    }
    await this.syncAll();
  }

  /**
   * Get pending sync count
   */
  async getPendingCount(): Promise<number> {
    const syncQueue = await offlineStorage.getSyncQueue();
    return syncQueue.length;
  }

  /**
   * Clear all offline data
   */
  async clearOfflineData(): Promise<void> {
    await offlineStorage.clear(STORES.REMINDERS);
    await offlineStorage.clear(STORES.ROUTINES);
    await offlineStorage.clear(STORES.MEDICATIONS);
    await offlineStorage.clear(STORES.HEALTH_METRICS);
    await offlineStorage.clear(STORES.ASSESSMENTS);
    await offlineStorage.clear(STORES.SYNC_QUEUE);
    await offlineStorage.clear(STORES.USER_DATA);
    console.log('All offline data cleared');
  }
}

// Export singleton instance
export const syncService = new SyncService();
