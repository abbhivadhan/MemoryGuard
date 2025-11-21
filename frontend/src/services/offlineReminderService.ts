/**
 * Offline Reminder Service
 * Manages reminders that work without internet connectivity
 */

import { offlineStorage, STORES } from './offlineStorage';

export interface OfflineReminder {
  id: string;
  userId: string;
  title: string;
  description?: string;
  time: string; // ISO string
  type: 'medication' | 'appointment' | 'routine' | 'custom';
  recurring?: 'daily' | 'weekly' | 'monthly';
  completed: boolean;
  notified: boolean;
  createdAt: string;
  updatedAt: string;
}

class OfflineReminderService {
  private notificationPermission: NotificationPermission = 'default';
  private checkInterval: number | null = null;

  constructor() {
    this.init();
  }

  /**
   * Initialize the offline reminder service
   */
  async init(): Promise<void> {
    await offlineStorage.init();
    
    // Request notification permission
    if ('Notification' in window) {
      this.notificationPermission = await Notification.requestPermission();
    }

    // Start checking for due reminders
    this.startReminderCheck();
  }

  /**
   * Create a new reminder
   */
  async createReminder(reminder: Omit<OfflineReminder, 'id' | 'createdAt' | 'updatedAt' | 'completed' | 'notified'>): Promise<OfflineReminder> {
    const newReminder: OfflineReminder = {
      ...reminder,
      id: `reminder-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      completed: false,
      notified: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    await offlineStorage.put(STORES.REMINDERS, newReminder);
    
    // Add to sync queue if online
    if (navigator.onLine) {
      await offlineStorage.addToSyncQueue({
        type: 'create',
        store: STORES.REMINDERS,
        data: newReminder,
      });
    }

    return newReminder;
  }

  /**
   * Get all reminders for a user
   */
  async getReminders(userId: string): Promise<OfflineReminder[]> {
    const reminders = await offlineStorage.getByIndex<OfflineReminder>(
      STORES.REMINDERS,
      'userId',
      userId
    );
    return reminders.sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime());
  }

  /**
   * Get upcoming reminders (next 24 hours)
   */
  async getUpcomingReminders(userId: string): Promise<OfflineReminder[]> {
    const allReminders = await this.getReminders(userId);
    const now = Date.now();
    const tomorrow = now + 24 * 60 * 60 * 1000;

    return allReminders.filter(reminder => {
      const reminderTime = new Date(reminder.time).getTime();
      return reminderTime >= now && reminderTime <= tomorrow && !reminder.completed;
    });
  }

  /**
   * Mark reminder as completed
   */
  async completeReminder(reminderId: string): Promise<void> {
    const reminder = await offlineStorage.get<OfflineReminder>(STORES.REMINDERS, reminderId);
    
    if (reminder) {
      reminder.completed = true;
      reminder.updatedAt = new Date().toISOString();
      await offlineStorage.put(STORES.REMINDERS, reminder);

      // Add to sync queue
      if (navigator.onLine) {
        await offlineStorage.addToSyncQueue({
          type: 'update',
          store: STORES.REMINDERS,
          data: reminder,
        });
      }
    }
  }

  /**
   * Delete a reminder
   */
  async deleteReminder(reminderId: string): Promise<void> {
    await offlineStorage.delete(STORES.REMINDERS, reminderId);

    // Add to sync queue
    if (navigator.onLine) {
      await offlineStorage.addToSyncQueue({
        type: 'delete',
        store: STORES.REMINDERS,
        data: { id: reminderId },
      });
    }
  }

  /**
   * Check for due reminders and send notifications
   */
  private async checkDueReminders(): Promise<void> {
    try {
      // Get all reminders from storage
      const allReminders = await offlineStorage.getAll<OfflineReminder>(STORES.REMINDERS);
      const now = Date.now();

      for (const reminder of allReminders) {
        if (reminder.completed || reminder.notified) continue;

        const reminderTime = new Date(reminder.time).getTime();
        
        // Check if reminder is due (within 1 minute)
        if (reminderTime <= now && reminderTime > now - 60000) {
          await this.sendNotification(reminder);
          
          // Mark as notified
          reminder.notified = true;
          reminder.updatedAt = new Date().toISOString();
          await offlineStorage.put(STORES.REMINDERS, reminder);
        }
      }
    } catch (error) {
      console.error('Error checking due reminders:', error);
    }
  }

  /**
   * Send notification for a reminder
   */
  private async sendNotification(reminder: OfflineReminder): Promise<void> {
    if (this.notificationPermission !== 'granted') return;

    try {
      const notification = new Notification(reminder.title, {
        body: reminder.description || 'You have a reminder',
        icon: '/icon-192x192.png',
        badge: '/icon-192x192.png',
        tag: reminder.id,
        requireInteraction: true,
      });

      notification.onclick = () => {
        window.focus();
        notification.close();
      };

      // Play audio alert
      this.playAudioAlert();
    } catch (error) {
      console.error('Error sending notification:', error);
    }
  }

  /**
   * Play audio alert
   */
  private playAudioAlert(): void {
    try {
      const audio = new Audio('/notification.mp3');
      audio.volume = 0.5;
      audio.play().catch(err => console.error('Error playing audio:', err));
    } catch (error) {
      console.error('Error creating audio:', error);
    }
  }

  /**
   * Start periodic reminder check
   */
  private startReminderCheck(): void {
    // Check every 30 seconds
    this.checkInterval = window.setInterval(() => {
      this.checkDueReminders();
    }, 30000);

    // Initial check
    this.checkDueReminders();
  }

  /**
   * Stop reminder check
   */
  stopReminderCheck(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
  }

  /**
   * Sync reminders with server when online
   */
  async syncWithServer(apiClient: any): Promise<void> {
    if (!navigator.onLine) return;

    try {
      // Get sync queue
      const syncQueue = await offlineStorage.getSyncQueue();
      const reminderItems = syncQueue.filter(item => item.store === STORES.REMINDERS);

      for (const item of reminderItems) {
        try {
          switch (item.type) {
            case 'create':
              await apiClient.post('/api/v1/reminders', item.data);
              break;
            case 'update':
              await apiClient.put(`/api/v1/reminders/${item.data.id}`, item.data);
              break;
            case 'delete':
              await apiClient.delete(`/api/v1/reminders/${item.data.id}`);
              break;
          }
        } catch (error) {
          console.error('Error syncing reminder:', error);
        }
      }

      // Clear synced items from queue
      await offlineStorage.clearSyncQueue();
    } catch (error) {
      console.error('Error syncing reminders:', error);
    }
  }
}

// Export singleton instance
export const offlineReminderService = new OfflineReminderService();
