/**
 * Lazy Loading Utilities
 * Provides utilities for code splitting and lazy loading
 * Requirements: 10.5
 */

import { lazy, ComponentType } from 'react';

/**
 * Retry lazy loading with exponential backoff
 * Useful for handling network failures
 */
export const lazyWithRetry = <T extends ComponentType<any>>(
  componentImport: () => Promise<{ default: T }>,
  retries = 3,
  interval = 1000
): React.LazyExoticComponent<T> => {
  return lazy(() => {
    return new Promise<{ default: T }>((resolve, reject) => {
      const attemptLoad = (attemptsLeft: number) => {
        componentImport()
          .then(resolve)
          .catch((error) => {
            if (attemptsLeft === 1) {
              reject(error);
              return;
            }
            
            setTimeout(() => {
              attemptLoad(attemptsLeft - 1);
            }, interval);
          });
      };
      
      attemptLoad(retries);
    });
  });
};

/**
 * Preload a lazy component
 * Useful for prefetching components before they're needed
 */
export const preloadComponent = (
  componentImport: () => Promise<any>
): void => {
  componentImport();
};
