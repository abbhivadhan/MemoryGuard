import { useEffect, useRef } from 'react';

interface DataWaveProps {
  color?: string;
  amplitude?: number;
  frequency?: number;
  speed?: number;
  opacity?: number;
}

/**
 * Animated wave visualization using canvas
 * Creates smooth, physics-based wave animations for data visualization
 */
export default function DataWave({
  color = '#06b6d4',
  amplitude = 30,
  frequency = 0.02,
  speed = 0.05,
  opacity = 0.3
}: DataWaveProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number>();
  const phaseRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      const parent = canvas.parentElement;
      if (parent) {
        canvas.width = parent.clientWidth;
        canvas.height = parent.clientHeight;
      }
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Animation loop
    const animate = () => {
      if (!ctx || !canvas) return;

      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Update phase for animation
      phaseRef.current += speed;

      // Draw wave
      ctx.beginPath();
      ctx.moveTo(0, canvas.height / 2);

      for (let x = 0; x < canvas.width; x++) {
        const y =
          canvas.height / 2 +
          Math.sin(x * frequency + phaseRef.current) * amplitude;
        ctx.lineTo(x, y);
      }

      // Create gradient
      const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
      gradient.addColorStop(0, `${color}00`);
      gradient.addColorStop(0.5, color);
      gradient.addColorStop(1, `${color}00`);

      ctx.strokeStyle = gradient;
      ctx.lineWidth = 2;
      ctx.globalAlpha = opacity;
      ctx.stroke();

      // Fill area under wave
      ctx.lineTo(canvas.width, canvas.height);
      ctx.lineTo(0, canvas.height);
      ctx.closePath();

      const fillGradient = ctx.createLinearGradient(
        0,
        canvas.height / 2 - amplitude,
        0,
        canvas.height
      );
      fillGradient.addColorStop(0, `${color}40`);
      fillGradient.addColorStop(1, `${color}00`);

      ctx.fillStyle = fillGradient;
      ctx.globalAlpha = opacity * 0.5;
      ctx.fill();

      ctx.globalAlpha = 1;
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    // Cleanup
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [color, amplitude, frequency, speed, opacity]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none"
    />
  );
}
