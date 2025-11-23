/**
 * Performance Monitor Component
 * Displays real-time performance metrics in development mode
 */
import React, { useState } from 'react';
import { usePerformance } from '../../hooks/usePerformance';

interface PerformanceMonitorProps {
  enabled?: boolean;
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
}

export const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  enabled = import.meta.env.DEV,
  position = 'bottom-right',
}) => {
  const { metrics, threeDMetrics } = usePerformance();
  const [isExpanded, setIsExpanded] = useState(false);

  if (!enabled) return null;

  const positionClasses = {
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4',
  };

  const getFPSColor = (fps: number) => {
    if (fps >= 55) return 'text-green-500';
    if (fps >= 30) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getMetricColor = (value: number, threshold: number, inverse = false) => {
    if (inverse) {
      return value <= threshold ? 'text-green-500' : 'text-red-500';
    }
    return value >= threshold ? 'text-green-500' : 'text-red-500';
  };

  return (
    <div
      className={`fixed ${positionClasses[position]} z-50 bg-black/80 text-white rounded-lg shadow-lg backdrop-blur-sm`}
      style={{ fontFamily: 'monospace', fontSize: '12px' }}
    >
      <div
        className="px-3 py-2 cursor-pointer flex items-center justify-between gap-2"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className={getFPSColor(metrics.fps)}>
          FPS: {metrics.fps}
        </span>
        <span className="text-gray-400">
          {isExpanded ? '▼' : '▶'}
        </span>
      </div>

      {isExpanded && (
        <div className="px-3 pb-3 space-y-1 border-t border-gray-700 pt-2">
          <div className="text-xs text-gray-400 font-bold mb-2">Core Web Vitals</div>
          
          <div className="flex justify-between gap-4">
            <span className="text-gray-400">LCP:</span>
            <span className={getMetricColor(metrics.largestContentfulPaint, 2500, true)}>
              {metrics.largestContentfulPaint.toFixed(0)}ms
            </span>
          </div>

          <div className="flex justify-between gap-4">
            <span className="text-gray-400">FID:</span>
            <span className={getMetricColor(metrics.firstInputDelay, 100, true)}>
              {metrics.firstInputDelay.toFixed(0)}ms
            </span>
          </div>

          <div className="flex justify-between gap-4">
            <span className="text-gray-400">CLS:</span>
            <span className={getMetricColor(metrics.cumulativeLayoutShift, 0.1, true)}>
              {metrics.cumulativeLayoutShift.toFixed(3)}
            </span>
          </div>

          <div className="text-xs text-gray-400 font-bold mt-3 mb-2">Page Load</div>

          <div className="flex justify-between gap-4">
            <span className="text-gray-400">Load:</span>
            <span>{(metrics.loadTime / 1000).toFixed(2)}s</span>
          </div>

          <div className="flex justify-between gap-4">
            <span className="text-gray-400">FCP:</span>
            <span>{metrics.firstContentfulPaint.toFixed(0)}ms</span>
          </div>

          {metrics.memoryUsage && (
            <>
              <div className="text-xs text-gray-400 font-bold mt-3 mb-2">Memory</div>
              <div className="flex justify-between gap-4">
                <span className="text-gray-400">Used:</span>
                <span className={getMetricColor(metrics.memoryUsage, 500, true)}>
                  {metrics.memoryUsage.toFixed(0)}MB
                </span>
              </div>
            </>
          )}

          {(threeDMetrics.drawCalls > 0 || threeDMetrics.triangles > 0) && (
            <>
              <div className="text-xs text-gray-400 font-bold mt-3 mb-2">3D Rendering</div>
              
              <div className="flex justify-between gap-4">
                <span className="text-gray-400">Draw Calls:</span>
                <span className={getMetricColor(threeDMetrics.drawCalls, 100, true)}>
                  {threeDMetrics.drawCalls}
                </span>
              </div>

              <div className="flex justify-between gap-4">
                <span className="text-gray-400">Triangles:</span>
                <span>{threeDMetrics.triangles.toLocaleString()}</span>
              </div>

              <div className="flex justify-between gap-4">
                <span className="text-gray-400">Geometries:</span>
                <span>{threeDMetrics.geometries}</span>
              </div>

              <div className="flex justify-between gap-4">
                <span className="text-gray-400">Textures:</span>
                <span>{threeDMetrics.textures}</span>
              </div>
            </>
          )}

          <div className="text-xs text-gray-500 mt-3 pt-2 border-t border-gray-700">
            Click to collapse
          </div>
        </div>
      )}
    </div>
  );
};

export default PerformanceMonitor;
