import { useEffect, useRef, useState } from 'react';

interface ScrollSectionProps {
  onDeteriorationChange?: (value: number) => void;
  onSectionChange?: (section: number) => void;
}

/**
 * Scroll-triggered animation sequence showing disease progression
 * Uses Intersection Observer to trigger animations
 */
export default function ScrollSection({ 
  onDeteriorationChange,
  onSectionChange 
}: ScrollSectionProps) {
  const [activeSection, setActiveSection] = useState(0);
  const sectionsRef = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    const observers: IntersectionObserver[] = [];

    sectionsRef.current.forEach((section, index) => {
      if (!section) return;

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              setActiveSection(index);
              // Update brain deterioration based on section
              if (onDeteriorationChange) {
                onDeteriorationChange(index * 0.25);
              }
              if (onSectionChange) {
                onSectionChange(index);
              }
            }
          });
        },
        {
          threshold: 0.5,
          rootMargin: '-20% 0px -20% 0px',
        }
      );

      observer.observe(section);
      observers.push(observer);
    });

    return () => {
      observers.forEach((observer) => observer.disconnect());
    };
  }, [onDeteriorationChange, onSectionChange]);

  const sections = [
    {
      title: 'Understanding Alzheimer\'s',
      description: 'Alzheimer\'s disease affects millions worldwide, progressively impacting memory, thinking, and behavior. Early awareness and support can help improve quality of life.',
      subtitle: 'A progressive neurodegenerative disorder',
      stats: ['Millions affected globally', 'Leading cause of dementia', 'Early awareness matters'],
      color: 'from-gray-900 via-indigo-950 to-black',
    },
    {
      title: 'Early Detection Support',
      description: 'Our platform uses machine learning to analyze patterns and provide insights. Always consult with healthcare professionals for medical diagnosis and treatment.',
      subtitle: 'AI-powered analysis tools',
      stats: ['Pattern analysis', 'Health insights', 'Professional guidance recommended'],
      color: 'from-black via-purple-950 to-gray-900',
    },
    {
      title: 'Comprehensive Monitoring',
      description: 'Track cognitive health over time with assessments, memory exercises, and health metrics. Share insights with your healthcare provider to support informed decisions.',
      subtitle: 'Continuous health tracking',
      stats: ['Cognitive assessments', 'Progress tracking', 'Personalized insights'],
      color: 'from-gray-900 via-blue-950 to-black',
    },
    {
      title: 'Complete Care Platform',
      description: 'MemoryGuard combines analysis tools with practical daily assistance features including medication reminders, memory aids, and caregiver support resources.',
      subtitle: 'Supporting patients & caregivers',
      stats: ['Daily assistance', 'Family connectivity', 'Support resources'],
      color: 'from-black via-indigo-950 to-gray-900',
    },
  ];

  return (
    <div className="relative">
      {sections.map((section, index) => (
        <div
          key={index}
          ref={(el) => (sectionsRef.current[index] = el)}
          className={`min-h-screen flex items-center justify-center bg-gradient-to-br ${section.color} 
            transition-all duration-1000 relative overflow-hidden`}
        >
          <div className={`max-w-4xl px-8 text-center transform transition-all duration-1000 ${
            activeSection === index 
              ? 'translate-y-0 opacity-100' 
              : 'translate-y-20 opacity-0'
          }`}>
            <div className="space-y-8">
              <h2 className="text-7xl font-bold text-white">
                {section.title}
              </h2>
              
              <p className="text-2xl text-gray-400 font-light">
                {section.subtitle}
              </p>
              
              <p className="text-xl text-gray-300 leading-relaxed max-w-3xl mx-auto">
                {section.description}
              </p>

              {/* Key stats */}
              <div className="flex flex-wrap justify-center gap-6 mt-8">
                {section.stats.map((stat, i) => (
                  <div 
                    key={i}
                    className="px-6 py-3 bg-white/5 backdrop-blur-sm rounded-lg border border-white/10"
                  >
                    <p className="text-sm text-gray-300 font-medium">{stat}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Progress indicator */}
            <div className="flex justify-center gap-3 mt-16">
              {sections.map((_, i) => (
                <div
                  key={i}
                  className={`h-1 rounded-full transition-all duration-500 ${
                    i === activeSection 
                      ? 'w-16 bg-indigo-500' 
                      : 'w-8 bg-gray-600'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Hook to track scroll progress
 */
export function useScrollProgress() {
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight - windowHeight;
      const scrolled = window.scrollY;
      const progress = scrolled / documentHeight;
      setScrollProgress(Math.min(Math.max(progress, 0), 1));
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Initial call

    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return scrollProgress;
}
