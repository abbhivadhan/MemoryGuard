/**
 * Responsive Container Component
 * Provides consistent responsive padding and max-width across all screen sizes
 * Requirements: 10.1
 */

import React from 'react';

interface ResponsiveContainerProps {
  children: React.ReactNode;
  className?: string;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
  noPadding?: boolean;
}

const maxWidthClasses = {
  sm: 'max-w-screen-sm',
  md: 'max-w-screen-md',
  lg: 'max-w-screen-lg',
  xl: 'max-w-screen-xl',
  '2xl': 'max-w-screen-2xl',
  full: 'max-w-full',
};

const ResponsiveContainer: React.FC<ResponsiveContainerProps> = ({
  children,
  className = '',
  maxWidth = 'xl',
  noPadding = false,
}) => {
  const paddingClass = noPadding ? '' : 'px-4 sm:px-6 lg:px-8';
  
  return (
    <div className={`w-full mx-auto ${maxWidthClasses[maxWidth]} ${paddingClass} ${className}`}>
      {children}
    </div>
  );
};

export default ResponsiveContainer;
