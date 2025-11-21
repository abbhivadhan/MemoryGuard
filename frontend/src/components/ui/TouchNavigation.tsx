/**
 * Touch-Optimized Navigation Component
 * Provides mobile-friendly navigation with touch gestures
 * Requirements: 10.3
 */

import React from 'react';
import { motion } from 'framer-motion';

interface TouchNavigationProps {
  items: Array<{
    label: string;
    icon?: React.ReactNode;
    onClick: () => void;
    active?: boolean;
  }>;
  position?: 'top' | 'bottom';
  className?: string;
}

const TouchNavigation: React.FC<TouchNavigationProps> = ({
  items,
  position = 'bottom',
  className = '',
}) => {
  const positionClass = position === 'bottom' ? 'bottom-0' : 'top-0';

  return (
    <nav
      className={`fixed left-0 right-0 ${positionClass} z-50 backdrop-blur-xl bg-black/30 border-t border-white/10 ${className}`}
    >
      <div className="flex justify-around items-center px-2 py-2 safe-bottom">
        {items.map((item, index) => (
          <motion.button
            key={index}
            whileTap={{ scale: 0.9 }}
            onClick={item.onClick}
            className={`
              flex flex-col items-center justify-center
              px-3 py-2 rounded-lg
              touch-target no-select
              transition-all duration-200
              ${item.active
                ? 'text-cyan-400 bg-white/10'
                : 'text-gray-400 hover:text-white'
              }
            `}
          >
            {item.icon && (
              <span className="mb-1">{item.icon}</span>
            )}
            <span className="text-xs font-medium">{item.label}</span>
          </motion.button>
        ))}
      </div>
    </nav>
  );
};

export default TouchNavigation;
