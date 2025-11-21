/**
 * Offline Storage Service using IndexedDB
 * Provides local storage for reminders, routines, medications, and health data
 */

const DB_NAME = 'MemoryGuardDB';
const DB_VERSION = 1;

// Store names
export const STORES = {
  REMINDERS: 'reminders',
  ROUTINES: 'routines',
  MEDICATIONS: 'medications',
  HEALTH_METRICS: 'healthMetrics',
  ASSESSMENTS: 'assessments',
  SYNC_QUEUE: 'syncQueue',
  USER_DATA: 'userData',
} as const;

interface SyncQueueItem {
  id: string;
  type: 'create' | 'update' | 'delete';
  store: string;
  data: any;
  timestamp: number;
}

class OfflineStorageService {
  private db: IDBDatabase | null = null;

  /**
   * Initialize IndexedDB
   */
  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Create object stores if they don't exist
        if (!db.objectStoreNames.contains(STORES.REMINDERS)) {
          const reminderStore = db.createObjectStore(STORES.REMINDERS, { keyPath: 'id' });
          reminderStore.createIndex('userId', 'userId', { unique: false });
          reminderStore.createIndex('time', 'time', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.ROUTINES)) {
          const routineStore = db.createObjectStore(STORES.ROUTINES, { keyPath: 'id' });
          routineStore.createIndex('userId', 'userId', { unique: false });
          routineStore.createIndex('date', 'date', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.MEDICATIONS)) {
          const medicationStore = db.createObjectStore(STORES.MEDICATIONS, { keyPath: 'id' });
          medicationStore.createIndex('userId', 'userId', { unique: false });
          medicationStore.createIndex('active', 'active', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.HEALTH_METRICS)) {
          const healthStore = db.createObjectStore(STORES.HEALTH_METRICS, { keyPath: 'id' });
          healthStore.createIndex('userId', 'userId', { unique: false });
          healthStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.ASSESSMENTS)) {
          const assessmentStore = db.createObjectStore(STORES.ASSESSMENTS, { keyPath: 'id' });
          assessmentStore.createIndex('userId', 'userId', { unique: false });
          assessmentStore.createIndex('completedAt', 'completedAt', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.SYNC_QUEUE)) {
          const syncStore = db.createObjectStore(STORES.SYNC_QUEUE, { keyPath: 'id' });
          syncStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.USER_DATA)) {
          db.createObjectStore(STORES.USER_DATA, { keyPath: 'id' });
        }
      };
    });
  }

  /**
   * Get data from a store
   */
  async get<T>(storeName: string, key: string): Promise<T | undefined> {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(storeName, 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.get(key);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get all data from a store
   */
  async getAll<T>(storeName: string): Promise<T[]> {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(storeName, 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.getAll();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get data by index
   */
  async getByIndex<T>(storeName: string, indexName: string, value: any): Promise<T[]> {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(storeName, 'readonly');
      const store = transaction.objectStore(storeName);
      const index = store.index(indexName);
      const request = index.getAll(value);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Put data into a store
   */
  async put<T>(storeName: string, data: T): Promise<void> {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.put(data);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Delete data from a store
   */
  async delete(storeName: string, key: string): Promise<void> {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.delete(key);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Clear all data from a store
   */
  async clear(storeName: string): Promise<void> {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.clear();

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Add item to sync queue
   */
  async addToSyncQueue(item: Omit<SyncQueueItem, 'id' | 'timestamp'>): Promise<void> {
    const queueItem: SyncQueueItem = {
      ...item,
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
    };

    await this.put(STORES.SYNC_QUEUE, queueItem);
  }

  /**
   * Get all items from sync queue
   */
  async getSyncQueue(): Promise<SyncQueueItem[]> {
    return this.getAll<SyncQueueItem>(STORES.SYNC_QUEUE);
  }

  /**
   * Clear sync queue
   */
  async clearSyncQueue(): Promise<void> {
    await this.clear(STORES.SYNC_QUEUE);
  }

  /**
   * Cache user data for offline access
   */
  async cacheUserData(userId: string, data: any): Promise<void> {
    await this.put(STORES.USER_DATA, { id: userId, ...data, cachedAt: Date.now() });
  }

  /**
   * Get cached user data
   */
  async getCachedUserData(userId: string): Promise<any> {
    return this.get(STORES.USER_DATA, userId);
  }
}

// Export singleton instance
export const offlineStorage = new OfflineStorageService();
