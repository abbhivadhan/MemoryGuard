/**
 * Offline Status Indicator Component
 * Displays connection status and sync information
 */

import { useOnlineStatus } from '../hooks/useOnlineStatus';
import { useSyncStatus } from '../hooks/useSyncStatus';
import { WifiOff, Wifi, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';
import { syncService } from '../services/syncService';

export default function OfflineIndicator() {
  const isOnline = useOnlineStatus();
  const syncStatus = useSyncStatus();

  const handleForceSync = async () => {
    try {
      await syncService.forceSyncNow();
    } catch (error) {
      console.error('Force sync failed:', error);
    }
  };

  // Only show indicator when offline, syncing, or there are pending items/errors
  if (isOnline && syncStatus.pendingItems === 0 && !syncStatus.isSyncing && syncStatus.errors.length === 0) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div
        className={`
          flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg backdrop-blur-sm
          ${isOnline 
            ? 'bg-green-500/90 text-white' 
            : 'bg-orange-500/90 text-white'
          }
          transition-all duration-300 ease-in-out
        `}
      >
        {/* Status Icon */}
        <div className="flex-shrink-0">
          {!isOnline ? (
            <WifiOff className="w-5 h-5" />
          ) : syncStatus.isSyncing ? (
            <RefreshCw className="w-5 h-5 animate-spin" />
          ) : syncStatus.errors.length > 0 ? (
            <AlertCircle className="w-5 h-5" />
          ) : (
            <Wifi className="w-5 h-5" />
          )}
        </div>

        {/* Status Text */}
        <div className="flex-1 min-w-0">
          {!isOnline ? (
            <div>
              <p className="text-sm font-semibold">Offline Mode</p>
              <p className="text-xs opacity-90">Changes will sync when online</p>
            </div>
          ) : syncStatus.isSyncing ? (
            <div>
              <p className="text-sm font-semibold">Syncing...</p>
              <p className="text-xs opacity-90">
                {syncStatus.pendingItems} item{syncStatus.pendingItems !== 1 ? 's' : ''} remaining
              </p>
            </div>
          ) : syncStatus.pendingItems > 0 ? (
            <div>
              <p className="text-sm font-semibold">Pending Sync</p>
              <p className="text-xs opacity-90">
                {syncStatus.pendingItems} item{syncStatus.pendingItems !== 1 ? 's' : ''} to sync
              </p>
            </div>
          ) : syncStatus.errors.length > 0 ? (
            <div>
              <p className="text-sm font-semibold">Sync Error</p>
              <p className="text-xs opacity-90">Failed to sync some items</p>
            </div>
          ) : null}
        </div>

        {/* Action Button */}
        {isOnline && syncStatus.pendingItems > 0 && !syncStatus.isSyncing && (
          <button
            onClick={handleForceSync}
            className="flex-shrink-0 p-2 hover:bg-white/20 rounded-md transition-colors"
            title="Sync now"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Error Details */}
      {syncStatus.errors.length > 0 && (
        <div className="mt-2 p-3 bg-red-500/90 text-white rounded-lg shadow-lg backdrop-blur-sm">
          <p className="text-xs font-semibold mb-1">Sync Errors:</p>
          {syncStatus.errors.slice(0, 3).map((error, index) => (
            <p key={index} className="text-xs opacity-90 truncate">
              • {error}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
