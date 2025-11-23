import React, { useRef, useState } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';

interface PhysicsCardProps {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  onClick: () => void;
  gradient: string;
}

/**
 * Physics-based interactive card with 3D tilt effect
 * Uses real physics for smooth, natural animations
 */
function PhysicsCard({
  title,
  description,
  icon,
  onClick,
  gradient
}: PhysicsCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  // Motion values for mouse position
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  // Spring physics for smooth animations
  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [10, -10]), {
    stiffness: 300,
    damping: 30
  });
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-10, 10]), {
    stiffness: 300,
    damping: 30
  });

  // Glow effect based on mouse position
  const glowX = useSpring(useTransform(mouseX, [-0.5, 0.5], [0, 100]), {
    stiffness: 200,
    damping: 25
  });
  const glowY = useSpring(useTransform(mouseY, [-0.5, 0.5], [0, 100]), {
    stiffness: 200,
    damping: 25
  });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;

    const rect = cardRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    // Normalize mouse position relative to card center
    const x = (e.clientX - centerX) / (rect.width / 2);
    const y = (e.clientY - centerY) / (rect.height / 2);

    mouseX.set(x);
    mouseY.set(y);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    mouseX.set(0);
    mouseY.set(0);
  };

  return (
    <motion.div
      ref={cardRef}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      style={{
        rotateX,
        rotateY,
        transformStyle: 'preserve-3d'
      }}
      whileTap={{ scale: 0.95 }}
      className="relative cursor-pointer group"
    >
      {/* Card container with glass morphism */}
      <motion.div
        className="relative overflow-hidden rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 p-6 h-full"
        animate={{
          borderColor: isHovered ? 'rgba(255, 255, 255, 0.3)' : 'rgba(255, 255, 255, 0.1)'
        }}
        transition={{ duration: 0.3 }}
      >
        {/* Animated gradient background */}
        <motion.div
          className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0`}
          animate={{
            opacity: isHovered ? 0.15 : 0
          }}
          transition={{ duration: 0.3 }}
        />

        {/* Mouse-following glow effect */}
        <motion.div
          className="absolute w-64 h-64 rounded-full blur-3xl pointer-events-none"
          style={{
            background: `radial-gradient(circle, rgba(99, 102, 241, 0.3) 0%, transparent 70%)`,
            left: glowX,
            top: glowY,
            x: '-50%',
            y: '-50%'
          }}
          animate={{
            opacity: isHovered ? 1 : 0
          }}
        />

        {/* Content */}
        <div className="relative z-10" style={{ transform: 'translateZ(20px)' }}>
          {/* Icon with physics animation */}
          <motion.div
            className="mb-4 w-12 h-12 text-blue-50"
            animate={{
              scale: isHovered ? 1.1 : 1,
              rotate: isHovered ? 5 : 0
            }}
            transition={{
              type: 'spring',
              stiffness: 400,
              damping: 20
            }}
          >
            {icon}
          </motion.div>

          {/* Title */}
          <h3 className="text-xl font-bold mb-2 text-white">
            {title}
          </h3>

          {/* Description */}
          <p className="text-gray-400 text-sm leading-relaxed">
            {description}
          </p>

          {/* Animated arrow */}
          <motion.div
            className="mt-4 flex justify-end"
            animate={{
              x: isHovered ? 5 : 0
            }}
            transition={{
              type: 'spring',
              stiffness: 400,
              damping: 20
            }}
          >
            <svg
              className="w-6 h-6 text-blue-50"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7l5 5m0 0l-5 5m5-5H6"
              />
            </svg>
          </motion.div>
        </div>

        {/* Shimmer effect on hover */}
        <motion.div
          className="absolute inset-0 pointer-events-none"
          style={{
            background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent)',
            transform: 'translateX(-100%)'
          }}
          animate={{
            x: isHovered ? ['0%', '200%'] : '0%'
          }}
          transition={{
            duration: 1,
            ease: 'easeInOut',
            repeat: isHovered ? Infinity : 0,
            repeatDelay: 0.5
          }}
        />
      </motion.div>

      {/* Shadow effect */}
      <motion.div
        className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${gradient} blur-xl -z-10`}
        animate={{
          opacity: isHovered ? 0.3 : 0
        }}
        transition={{ duration: 0.3 }}
      />
    </motion.div>
  );
}

export default PhysicsCard;
