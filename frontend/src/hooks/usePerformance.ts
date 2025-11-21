/**
 * usePerformance Hook
 * Monitors and reports performance metrics
 * Requirements: 10.5
 */

import { useEffect, useState } from 'react';

interface PerformanceMetrics {
  fps: number;
  loadTime: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  timeToInteractive: number;
}

export const usePerformance = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    fps: 0,
    loadTime: 0,
    firstContentfulPaint: 0,
    largestContentfulPaint: 0,
    timeToInteractive: 0,
  });

  useEffect(() => {
    // Measure FPS
    let frameCount = 0;
    let lastTime = performance.now();
    let fps = 0;

    const measureFPS = () => {
      frameCount++;
      const currentTime = performance.now();
      
      if (currentTime >= lastTime + 1000) {
        fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
        frameCount = 0;
        lastTime = currentTime;
        
        setMetrics((prev) => ({ ...prev, fps }));
      }
      
      requestAnimationFrame(measureFPS);
    };

    const fpsId = requestAnimationFrame(measureFPS);

    // Get performance timing
    if (window.performance && window.performance.timing) {
      const timing = window.performance.timing;
      const loadTime = timing.loadEventEnd - timing.navigationStart;
      
      setMetrics((prev) => ({ ...prev, loadTime }));
    }

    // Get paint timing
    if (window.performance && window.performance.getEntriesByType) {
      const paintEntries = window.performance.getEntriesByType('paint');
      
      paintEntries.forEach((entry) => {
        if (entry.name === 'first-contentful-paint') {
          setMetrics((prev) => ({
            ...prev,
            firstContentfulPaint: entry.startTime,
          }));
        }
      });

      // Get LCP
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        
        setMetrics((prev) => ({
          ...prev,
          largestContentfulPaint: lastEntry.startTime,
        }));
      });

      try {
        observer.observe({ entryTypes: ['largest-contentful-paint'] });
      } catch (e) {
        // LCP not supported
      }

      return () => {
        cancelAnimationFrame(fpsId);
        observer.disconnect();
      };
    }

    return () => {
      cancelAnimationFrame(fpsId);
    };
  }, []);

  return metrics;
};
