# Offline Functionality Implementation

## Overview

MemoryGuard now includes comprehensive offline functionality that allows users to access critical features without an internet connection. This implementation ensures that essential features like reminders, emergency alerts, and daily routines continue to work even when connectivity is lost.

## Features Implemented

### 1. Service Worker with Workbox

**Location:** `frontend/vite.config.ts`, `frontend/src/main.tsx`

- Configured Vite PWA plugin with Workbox for automatic service worker generation
- Caches essential assets (JS, CSS, HTML, images, fonts)
- Implements runtime caching strategies:
  - **CacheFirst** for fonts and static assets
  - **NetworkFirst** for API calls (reminders, routines, medications)
- Automatic updates with user confirmation
- Offline-ready notification

**Key Configuration:**
```typescript
VitePWA({
  registerType: 'autoUpdate',
  workbox: {
    runtimeCaching: [
      {
        urlPattern: /\/api\/v1\/(reminders|routines|medications)/i,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'api-cache',
          networkTimeoutSeconds: 10
        }
      }
    ]
  }
})
```

### 2. IndexedDB Offline Storage

**Location:** `frontend/src/services/offlineStorage.ts`

Provides local storage for:
- Reminders
- Daily routines
- Medications
- Health metrics
- Cognitive assessments
- Sync queue for pending changes
- User data cache

**Key Features:**
- Indexed queries for efficient data retrieval
- Automatic sync queue management
- Support for create, read, update, delete operations
- Data persistence across sessions

**Usage Example:**
```typescript
import { offlineStorage, STORES } from './services/offlineStorage';

// Store a reminder
await offlineStorage.put(STORES.REMINDERS, reminderData);

// Get all reminders for a user
const reminders = await offlineStorage.getByIndex(
  STORES.REMINDERS, 
  'userId', 
  userId
);
```

### 3. Offline Reminder System

**Location:** `frontend/src/services/offlineReminderService.ts`

- Creates and manages reminders that work offline
- Periodic checking for due reminders (every 30 seconds)
- Browser notifications with audio alerts
- Automatic sync queue management
- Support for recurring reminders

**Key Features:**
- Works completely offline
- Visual and audio notifications
- Vibration support on mobile devices
- Automatic sync when connection restored

**Usage Example:**
```typescript
import { offlineReminderService } from './services/offlineReminderService';

// Create a reminder
const reminder = await offlineReminderService.createReminder({
  userId: 'user-123',
  title: 'Take medication',
  time: '2025-11-18T14:00:00Z',
  type: 'medication'
});

// Get upcoming reminders
const upcoming = await offlineReminderService.getUpcomingReminders('user-123');
```

### 4. Data Synchronization Service

**Location:** `frontend/src/services/syncService.ts`

- Automatic sync when connection restored
- Periodic sync every 10 seconds when online
- Sync queue management
- Error handling and retry logic
- Data caching for offline use

**Key Features:**
- Detects online/offline events
- Groups sync operations by store
- Provides sync status updates
- Supports force sync
- Clears sync queue after successful sync

**Usage Example:**
```typescript
import { syncService } from './services/syncService';

// Subscribe to sync status
const unsubscribe = syncService.subscribe((status) => {
  console.log('Sync status:', status);
});

// Force sync now
await syncService.forceSyncNow();

// Cache data for offline use
await syncService.cacheData(userId);
```

### 5. Offline Status Indicator

**Location:** `frontend/src/components/OfflineIndicator.tsx`

Visual indicator showing:
- Online/offline status
- Sync progress
- Pending items count
- Sync errors
- Last sync time

**Features:**
- Fixed position (bottom-right corner)
- Color-coded status (green=online, orange=offline)
- Animated sync icon
- Force sync button
- Auto-hide when online with no pending items

### 6. Offline Emergency Features

**Location:** `frontend/src/services/offlineEmergencyService.ts`

Emergency features that work without internet:
- Emergency alert activation
- GPS location capture
- Emergency contact notification via SMS/phone
- Device vibration (SOS pattern)
- Browser notifications
- Safe return home directions
- Emergency medical information storage

**Key Features:**
- Uses device capabilities (tel:, sms: protocols)
- Geolocation API for location
- Vibration API for alerts
- Notification API for alerts
- Stores alerts in sync queue

**Usage Example:**
```typescript
import { offlineEmergencyService } from './services/offlineEmergencyService';

// Trigger emergency alert
const alert = await offlineEmergencyService.triggerEmergencyAlert(userId);

// Get safe return home directions
const directions = await offlineEmergencyService.getSafeReturnHome(homeAddress);

// Cache emergency contacts
await offlineEmergencyService.cacheEmergencyContacts(userId, contacts);
```

## Custom Hooks

### useOnlineStatus

**Location:** `frontend/src/hooks/useOnlineStatus.ts`

Tracks online/offline status in React components.

```typescript
import { useOnlineStatus } from './hooks/useOnlineStatus';

function MyComponent() {
  const isOnline = useOnlineStatus();
  
  return <div>{isOnline ? 'Online' : 'Offline'}</div>;
}
```

### useSyncStatus

**Location:** `frontend/src/hooks/useSyncStatus.ts`

Tracks sync status in React components.

```typescript
import { useSyncStatus } from './hooks/useSyncStatus';

function MyComponent() {
  const syncStatus = useSyncStatus();
  
  return (
    <div>
      {syncStatus.isSyncing && 'Syncing...'}
      {syncStatus.pendingItems > 0 && `${syncStatus.pendingItems} pending`}
    </div>
  );
}
```

## Integration

The offline functionality is integrated into the main App component:

```typescript
// frontend/src/App.tsx
import OfflineIndicator from './components/OfflineIndicator';

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
```

## Testing Offline Functionality

### 1. Test Service Worker

1. Build the app: `npm run build`
2. Serve the build: `npm run preview`
3. Open DevTools > Application > Service Workers
4. Verify service worker is registered and active

### 2. Test Offline Mode

1. Open the app in browser
2. Open DevTools > Network tab
3. Select "Offline" from throttling dropdown
4. Verify:
   - Offline indicator appears
   - Cached pages still load
   - Reminders still work
   - Emergency button still functions

### 3. Test Data Sync

1. Go offline
2. Create/update data (reminders, routines, etc.)
3. Go back online
4. Verify:
   - Sync indicator shows syncing
   - Data syncs to server
   - Sync queue clears

### 4. Test Emergency Features

1. Go offline
2. Click emergency button
3. Verify:
   - Location is captured
   - Notification appears
   - Device vibrates
   - SMS/call links open

## Browser Support

- **Service Workers:** Chrome 40+, Firefox 44+, Safari 11.1+, Edge 17+
- **IndexedDB:** All modern browsers
- **Notifications:** Chrome 22+, Firefox 22+, Safari 7+, Edge 14+
- **Geolocation:** All modern browsers
- **Vibration:** Chrome 32+, Firefox 16+, Edge 79+ (mobile only)

## Performance Considerations

- Service worker caches are limited to ~50MB per origin
- IndexedDB storage is limited by browser (typically 50% of available disk space)
- Sync operations are throttled to prevent excessive API calls
- Reminder checks run every 30 seconds (configurable)
- Periodic sync runs every 10 seconds when online (configurable)

## Security Considerations

- All cached data is stored locally on the device
- Sync queue is cleared after successful sync
- Emergency medical information is encrypted in IndexedDB
- Service worker only caches public assets
- API tokens are not cached in service worker

## Future Enhancements

1. **Background Sync API**: Use Background Sync API for more reliable syncing
2. **Push Notifications**: Server-initiated notifications for important events
3. **Conflict Resolution**: Handle conflicts when same data is modified offline and online
4. **Selective Sync**: Allow users to choose what data to cache
5. **Storage Management**: Implement storage quota management and cleanup
6. **Offline Analytics**: Track offline usage patterns
7. **Progressive Enhancement**: Graceful degradation for older browsers

## Troubleshooting

### Service Worker Not Registering

- Check browser console for errors
- Verify HTTPS is enabled (required for service workers)
- Clear browser cache and reload
- Check service worker scope in DevTools

### Data Not Syncing

- Check network connectivity
- Verify sync queue has items: `await syncService.getPendingCount()`
- Check browser console for sync errors
- Force sync: `await syncService.forceSyncNow()`

### Notifications Not Working

- Check notification permission: `Notification.permission`
- Request permission: `await Notification.requestPermission()`
- Verify notifications are enabled in browser settings

### IndexedDB Errors

- Check browser storage quota
- Clear IndexedDB: `await syncService.clearOfflineData()`
- Check browser console for specific errors

## Requirements Satisfied

This implementation satisfies the following requirements from the spec:

- **19.1**: Offline functionality with service worker and IndexedDB
- **19.2**: Offline reminder system with notifications
- **19.3**: Data synchronization when connectivity restored
- **19.4**: Offline status indicator
- **19.5**: Offline emergency features using device capabilities
- **19.6**: Automatic sync within 10 seconds of connectivity restoration

## Conclusion

The offline functionality implementation provides a robust, production-ready solution for ensuring MemoryGuard remains functional even without internet connectivity. Critical features like reminders, emergency alerts, and daily routines continue to work seamlessly, with automatic synchronization when connectivity is restored.
