/**
 * Sentry error tracking configuration for frontend
 * Simplified to prevent initialization issues
 */

/**
 * Initialize Sentry error tracking
 * Only enabled in production with a valid DSN
 */
export const initSentry = () => {
  const sentryDsn = import.meta.env.VITE_SENTRY_DSN;
  const environment = import.meta.env.MODE;
  
  if (!sentryDsn) {
    console.info('Sentry DSN not configured - error tracking disabled');
    return;
  }
  
  if (environment !== 'production' && !import.meta.env.VITE_SENTRY_ENABLED) {
    console.info('Sentry disabled in non-production environment');
    return;
  }

  // Lazy load Sentry to avoid blocking app startup
  import('@sentry/react').then((Sentry) => {
    try {
      Sentry.init({
        dsn: sentryDsn,
        environment,
        release: `memoryguard-frontend@${import.meta.env.VITE_APP_VERSION || '0.1.0'}`,
        
        // Performance monitoring
        tracesSampleRate: parseFloat(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE || '0.1'),
        
        // Error sampling
        sampleRate: 1.0,
        
        // Additional options
        attachStacktrace: true,
        sendDefaultPii: false, // HIPAA compliance
        maxBreadcrumbs: 50,
        
        // Ignore certain errors
        ignoreErrors: [
          'top.GLOBALS',
          'chrome-extension://',
          'moz-extension://',
          'NetworkError',
          'Failed to fetch',
          'WebGL context lost',
          'WEBGL_lose_context',
        ],
      });
      
      console.info(`Sentry initialized - Environment: ${environment}`);
    } catch (error) {
      console.error('Failed to initialize Sentry:', error);
    }
  }).catch((error) => {
    console.warn('Failed to load Sentry:', error);
  });
};

/**
 * Manually capture an exception with additional context
 */
export const captureException = (error: Error, context?: Record<string, any>) => {
  console.error('Exception:', error, context);
  
  import('@sentry/react').then((Sentry) => {
    Sentry.captureException(error);
  }).catch(() => {
    // Sentry not available
  });
};

/**
 * Manually capture a message with additional context
 */
export const captureMessage = (message: string, level: 'info' | 'warning' | 'error' = 'info', context?: Record<string, any>) => {
  console.log(`[${level}] ${message}`, context);
  
  import('@sentry/react').then((Sentry) => {
    Sentry.captureMessage(message, level as any);
  }).catch(() => {
    // Sentry not available
  });
};

/**
 * Set user context for error tracking
 */
export const setUserContext = (userId: string, email?: string) => {
  import('@sentry/react').then((Sentry) => {
    Sentry.setUser({
      id: userId,
      email: email || undefined,
    });
  }).catch(() => {
    // Sentry not available
  });
};

/**
 * Clear user context
 */
export const clearUserContext = () => {
  import('@sentry/react').then((Sentry) => {
    Sentry.setUser(null);
  }).catch(() => {
    // Sentry not available
  });
};

/**
 * Add breadcrumb for tracking user actions
 */
export const addBreadcrumb = (message: string, category: string, data?: Record<string, any>) => {
  import('@sentry/react').then((Sentry) => {
    Sentry.addBreadcrumb({
      message,
      category,
      level: 'info',
      data,
    });
  }).catch(() => {
    // Sentry not available
  });
};

export default { initSentry, captureException, captureMessage, setUserContext, clearUserContext, addBreadcrumb };
