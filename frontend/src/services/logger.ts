/**
 * Frontend logging service
 * Simple browser-compatible implementation
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

class Logger {
  private level: LogLevel = 'debug';

  private shouldLog(level: LogLevel): boolean {
    const levels: LogLevel[] = ['debug', 'info', 'warn', 'error'];
    const currentLevelIndex = levels.indexOf(this.level);
    const messageLevelIndex = levels.indexOf(level);
    return messageLevelIndex >= currentLevelIndex;
  }

  debug(message: string, metadata?: Record<string, any>): void {
    if (this.shouldLog('debug')) {
      console.debug(`[DEBUG] ${message}`, metadata || '');
    }
  }

  info(message: string, metadata?: Record<string, any>): void {
    if (this.shouldLog('info')) {
      console.info(`[INFO] ${message}`, metadata || '');
    }
  }

  warn(message: string, metadata?: Record<string, any>): void {
    if (this.shouldLog('warn')) {
      console.warn(`[WARN] ${message}`, metadata || '');
    }
  }

  error(message: string, metadata?: Record<string, any>): void {
    if (this.shouldLog('error')) {
      console.error(`[ERROR] ${message}`, metadata || '');
    }
  }

  log(level: LogLevel, message: string, metadata?: Record<string, any>): void {
    this[level](message, metadata);
  }
}

// Create logger instance
const logger = new Logger();

// Helper functions for common logging patterns
export const logError = (message: string, error: Error, metadata?: Record<string, any>) => {
  logger.error(message, {
    error: error.message,
    ...metadata,
  });
};

export const logPerformance = (operation: string, duration: number, metadata?: Record<string, any>) => {
  logger.info(`Performance: ${operation}`, {
    duration_ms: duration,
    ...metadata,
  });
};

export const logUserAction = (action: string, metadata?: Record<string, any>) => {
  logger.info(`User action: ${action}`, {
    action,
    ...metadata,
  });
};

export const logAPICall = (
  method: string,
  url: string,
  status: number,
  duration: number,
  metadata?: Record<string, any>
) => {
  const level = status >= 400 ? 'error' : 'info';
  logger.log(level, `API ${method} ${url}`, {
    method,
    url,
    status,
    duration_ms: duration,
    ...metadata,
  });
};

export const log3DPerformance = (
  scene: string,
  fps: number,
  drawCalls: number,
  triangles: number,
  metadata?: Record<string, any>
) => {
  logger.debug(`3D Performance: ${scene}`, {
    scene,
    fps,
    drawCalls,
    triangles,
    ...metadata,
  });
};

export default logger;
