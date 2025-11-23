

interface ScrollIndicatorProps {
  onClick?: () => void;
}

/**
 * Simple animated down arrow indicator
 */
export default function ScrollIndicator({ onClick }: ScrollIndicatorProps) {
  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      window.scrollTo({ 
        top: window.innerHeight, 
        behavior: 'smooth' 
      });
    }
  };

  return (
    <button
      onClick={handleClick}
      className="group transition-all duration-300 hover:scale-110 active:scale-95 cursor-pointer"
      aria-label="Scroll down for more information"
    >
      <svg
        className="w-8 h-8 text-cyan-400 group-hover:text-cyan-300 transition-colors animate-bounce"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M19 14l-7 7m0 0l-7-7m7 7V3"
        />
      </svg>
    </button>
  );
}
