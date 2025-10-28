'use client';

import { useEffect, useRef, useState, ReactNode } from 'react';

interface PerformanceWrapperProps {
  children: ReactNode;
  className?: string;
  pauseWhenHidden?: boolean;
}

export default function PerformanceWrapper({ 
  children, 
  className = '',
  pauseWhenHidden = true 
}: PerformanceWrapperProps) {
  const [isVisible, setIsVisible] = useState(true);
  const [isDocumentVisible, setIsDocumentVisible] = useState(true);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!pauseWhenHidden) return;

    const element = ref.current;
    if (!element) return;

    // Intersection Observer for viewport visibility
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          setIsVisible(entry.isIntersecting);
        });
      },
      { 
        threshold: 0.1,
        rootMargin: '50px' // Start loading slightly before entering viewport
      }
    );

    observer.observe(element);

    // Document visibility for tab switching
    const handleVisibilityChange = () => {
      setIsDocumentVisible(!document.hidden);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      observer.disconnect();
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [pauseWhenHidden]);

  const shouldRender = !pauseWhenHidden || (isVisible && isDocumentVisible);

  return (
    <div 
      ref={ref} 
      className={className}
      style={{
        opacity: shouldRender ? 1 : 0.3,
        transition: 'opacity 0.3s ease'
      }}
    >
      {shouldRender ? children : <div className="w-full h-full bg-black/20" />}
    </div>
  );
}