/**
 * Custom hook to track sync status
 */

import { useState, useEffect } from 'react';
import { syncService, SyncStatus } from '../services/syncService';

export function useSyncStatus() {
  const [syncStatus, setSyncStatus] = useState<SyncStatus>(syncService.getStatus());

  useEffect(() => {
    const unsubscribe = syncService.subscribe((status) => {
      setSyncStatus(status);
    });

    return unsubscribe;
  }, []);

  return syncStatus;
}
