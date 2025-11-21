/**
 * Resource Preloader Component
 * Preloads critical resources for better performance
 * Requirements: 10.5
 */

import { useEffect } from 'react';

interface ResourcePreloaderProps {
  images?: string[];
  fonts?: string[];
  scripts?: string[];
}

const ResourcePreloader: React.FC<ResourcePreloaderProps> = ({
  images = [],
  fonts = [],
  scripts = [],
}) => {
  useEffect(() => {
    // Preload images
    images.forEach((src) => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'image';
      link.href = src;
      document.head.appendChild(link);
    });

    // Preload fonts
    fonts.forEach((src) => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'font';
      link.type = 'font/woff2';
      link.href = src;
      link.crossOrigin = 'anonymous';
      document.head.appendChild(link);
    });

    // Preload scripts
    scripts.forEach((src) => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'script';
      link.href = src;
      document.head.appendChild(link);
    });
  }, [images, fonts, scripts]);

  return null;
};

export default ResourcePreloader;
