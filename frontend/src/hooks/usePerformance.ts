/**
 * usePerformance Hook
 * Monitors and reports performance metrics
 * Requirements: 10.5, 2.6, 7.3
 */

import { useEffect, useState, useCallback } from 'react';
import { logPerformance, log3DPerformance } from '../services/logger';

interface PerformanceMetrics {
  fps: number;
  loadTime: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  timeToInteractive: number;
  firstInputDelay: number;
  cumulativeLayoutShift: number;
  memoryUsage?: number;
}

interface ThreeDMetrics {
  drawCalls: number;
  triangles: number;
  geometries: number;
  textures: number;
}

export const usePerformance = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    fps: 0,
    loadTime: 0,
    firstContentfulPaint: 0,
    largestContentfulPaint: 0,
    timeToInteractive: 0,
    firstInputDelay: 0,
    cumulativeLayoutShift: 0,
  });

  const [threeDMetrics, setThreeDMetrics] = useState<ThreeDMetrics>({
    drawCalls: 0,
    triangles: 0,
    geometries: 0,
    textures: 0,
  });

  useEffect(() => {
    // Measure FPS
    let frameCount = 0;
    let lastTime = performance.now();
    let fps = 0;
    let reportedLowFPS = false;

    const measureFPS = () => {
      frameCount++;
      const currentTime = performance.now();
      
      if (currentTime >= lastTime + 1000) {
        fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
        frameCount = 0;
        lastTime = currentTime;
        
        setMetrics((prev) => ({ ...prev, fps }));
        
        // Log warning if FPS drops below 30
        if (fps < 30 && !reportedLowFPS) {
          logPerformance('Low FPS detected', fps, { threshold: 30 });
          reportedLowFPS = true;
        } else if (fps >= 30) {
          reportedLowFPS = false;
        }
      }
      
      requestAnimationFrame(measureFPS);
    };

    const fpsId = requestAnimationFrame(measureFPS);

    // Get performance timing
    if (window.performance && window.performance.timing) {
      const timing = window.performance.timing;
      const loadTime = timing.loadEventEnd - timing.navigationStart;
      
      if (loadTime > 0) {
        setMetrics((prev) => ({ ...prev, loadTime }));
        logPerformance('Page load', loadTime);
      }
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
          logPerformance('First Contentful Paint', entry.startTime);
        }
      });

      // Get LCP
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1] as any;
        
        setMetrics((prev) => ({
          ...prev,
          largestContentfulPaint: lastEntry.startTime,
        }));
        
        if (lastEntry.startTime > 2500) {
          logPerformance('Slow LCP detected', lastEntry.startTime, { threshold: 2500 });
        }
      });

      // Get FID
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          const fid = entry.processingStart - entry.startTime;
          setMetrics((prev) => ({
            ...prev,
            firstInputDelay: fid,
          }));
          
          if (fid > 100) {
            logPerformance('Slow FID detected', fid, { threshold: 100 });
          }
        });
      });

      // Get CLS
      let clsValue = 0;
      const clsObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
            setMetrics((prev) => ({
              ...prev,
              cumulativeLayoutShift: clsValue,
            }));
          }
        });
        
        if (clsValue > 0.1) {
          logPerformance('High CLS detected', clsValue, { threshold: 0.1 });
        }
      });

      try {
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        fidObserver.observe({ entryTypes: ['first-input'] });
        clsObserver.observe({ entryTypes: ['layout-shift'] });
      } catch (e) {
        // Some metrics not supported
        console.debug('Some performance metrics not supported:', e);
      }

      return () => {
        cancelAnimationFrame(fpsId);
        lcpObserver.disconnect();
        fidObserver.disconnect();
        clsObserver.disconnect();
      };
    }

    return () => {
      cancelAnimationFrame(fpsId);
    };
  }, []);

  // Monitor memory usage
  useEffect(() => {
    const checkMemory = () => {
      if ((performance as any).memory) {
        const memory = (performance as any).memory;
        const usedMemoryMB = memory.usedJSHeapSize / 1048576;
        
        setMetrics((prev) => ({
          ...prev,
          memoryUsage: usedMemoryMB,
        }));
        
        // Warn if memory usage is high
        if (usedMemoryMB > 500) {
          logPerformance('High memory usage', usedMemoryMB, { threshold: 500, unit: 'MB' });
        }
      }
    };

    const memoryInterval = setInterval(checkMemory, 10000); // Check every 10 seconds
    checkMemory();

    return () => clearInterval(memoryInterval);
  }, []);

  // Track 3D rendering performance
  const track3DPerformance = useCallback((
    scene: string,
    renderer: any
  ) => {
    if (renderer && renderer.info) {
      const info = renderer.info;
      const newMetrics = {
        drawCalls: info.render.calls,
        triangles: info.render.triangles,
        geometries: info.memory.geometries,
        textures: info.memory.textures,
      };
      
      setThreeDMetrics(newMetrics);
      
      // Log 3D performance
      log3DPerformance(
        scene,
        metrics.fps,
        newMetrics.drawCalls,
        newMetrics.triangles
      );
      
      // Warn if draw calls are high
      if (newMetrics.drawCalls > 100) {
        logPerformance('High draw calls', newMetrics.drawCalls, {
          scene,
          threshold: 100,
        });
      }
    }
  }, [metrics.fps]);

  // Measure component render time
  const measureRender = useCallback((componentName: string, callback: () => void) => {
    const startTime = performance.now();
    callback();
    const duration = performance.now() - startTime;
    
    if (duration > 16) { // Longer than one frame at 60fps
      logPerformance(`Slow render: ${componentName}`, duration, {
        component: componentName,
        threshold: 16,
      });
    }
  }, []);

  return {
    metrics,
    threeDMetrics,
    track3DPerformance,
    measureRender,
  };
};
