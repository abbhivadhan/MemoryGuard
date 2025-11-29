/**
 * useTouchGestures Hook
 * Provides touch gesture detection for mobile interactions
 * Requirements: 10.3
 */

import { useEffect, useRef, useState } from 'react';

interface TouchGestureState {
  isSwiping: boolean;
  isPinching: boolean;
  swipeDirection: 'left' | 'right' | 'up' | 'down' | null;
  pinchScale: number;
  touchCount: number;
}

interface TouchGestureHandlers {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onPinchIn?: (scale: number) => void;
  onPinchOut?: (scale: number) => void;
  onTap?: () => void;
  onDoubleTap?: () => void;
  onLongPress?: () => void;
}

export const useTouchGestures = (
  elementRef: React.RefObject<HTMLElement>,
  handlers: TouchGestureHandlers = {}
) => {
  const [state, setState] = useState<TouchGestureState>({
    isSwiping: false,
    isPinching: false,
    swipeDirection: null,
    pinchScale: 1,
    touchCount: 0,
  });

  const touchStartRef = useRef<{ x: number; y: number; time: number } | null>(null);
  const lastTapRef = useRef<number>(0);
  const longPressTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const initialPinchDistanceRef = useRef<number>(0);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const getDistance = (touch1: Touch, touch2: Touch): number => {
      const dx = touch1.clientX - touch2.clientX;
      const dy = touch1.clientY - touch2.clientY;
      return Math.sqrt(dx * dx + dy * dy);
    };

    const handleTouchStart = (e: TouchEvent) => {
      const touch = e.touches[0];
      const touchCount = e.touches.length;

      setState(prev => ({ ...prev, touchCount }));

      if (touchCount === 1) {
        touchStartRef.current = {
          x: touch.clientX,
          y: touch.clientY,
          time: Date.now(),
        };

        // Start long press timer
        longPressTimerRef.current = setTimeout(() => {
          handlers.onLongPress?.();
        }, 500);
      } else if (touchCount === 2) {
        // Pinch gesture
        initialPinchDistanceRef.current = getDistance(e.touches[0], e.touches[1]);
        setState(prev => ({ ...prev, isPinching: true }));
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      // Clear long press timer on move
      if (longPressTimerRef.current) {
        clearTimeout(longPressTimerRef.current);
        longPressTimerRef.current = null;
      }

      if (e.touches.length === 2 && initialPinchDistanceRef.current > 0) {
        // Handle pinch
        const currentDistance = getDistance(e.touches[0], e.touches[1]);
        const scale = currentDistance / initialPinchDistanceRef.current;
        
        setState(prev => ({ ...prev, pinchScale: scale }));

        if (scale > 1.1) {
          handlers.onPinchOut?.(scale);
        } else if (scale < 0.9) {
          handlers.onPinchIn?.(scale);
        }
      } else if (e.touches.length === 1 && touchStartRef.current) {
        // Handle swipe
        const touch = e.touches[0];
        const deltaX = touch.clientX - touchStartRef.current.x;
        const deltaY = touch.clientY - touchStartRef.current.y;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

        if (distance > 50) {
          setState(prev => ({ ...prev, isSwiping: true }));
        }
      }
    };

    const handleTouchEnd = (e: TouchEvent) => {
      // Clear long press timer
      if (longPressTimerRef.current) {
        clearTimeout(longPressTimerRef.current);
        longPressTimerRef.current = null;
      }

      if (e.changedTouches.length === 1 && touchStartRef.current) {
        const touch = e.changedTouches[0];
        const deltaX = touch.clientX - touchStartRef.current.x;
        const deltaY = touch.clientY - touchStartRef.current.y;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        const duration = Date.now() - touchStartRef.current.time;

        // Detect tap or double tap
        if (distance < 10 && duration < 300) {
          const now = Date.now();
          if (now - lastTapRef.current < 300) {
            handlers.onDoubleTap?.();
          } else {
            handlers.onTap?.();
          }
          lastTapRef.current = now;
        }

        // Detect swipe
        if (distance > 50 && duration < 500) {
          const angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI);
          let direction: 'left' | 'right' | 'up' | 'down';

          if (angle > -45 && angle <= 45) {
            direction = 'right';
            handlers.onSwipeRight?.();
          } else if (angle > 45 && angle <= 135) {
            direction = 'down';
            handlers.onSwipeDown?.();
          } else if (angle > -135 && angle <= -45) {
            direction = 'up';
            handlers.onSwipeUp?.();
          } else {
            direction = 'left';
            handlers.onSwipeLeft?.();
          }

          setState(prev => ({ ...prev, swipeDirection: direction }));
        }
      }

      // Reset state
      setState(prev => ({
        ...prev,
        isSwiping: false,
        isPinching: false,
        swipeDirection: null,
        pinchScale: 1,
        touchCount: 0,
      }));
      touchStartRef.current = null;
      initialPinchDistanceRef.current = 0;
    };

    element.addEventListener('touchstart', handleTouchStart, { passive: true });
    element.addEventListener('touchmove', handleTouchMove, { passive: true });
    element.addEventListener('touchend', handleTouchEnd, { passive: true });

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchend', handleTouchEnd);
      
      if (longPressTimerRef.current) {
        clearTimeout(longPressTimerRef.current);
      }
    };
  }, [elementRef, handlers]);

  return state;
};
