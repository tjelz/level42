'use client';

import { useState, useEffect, useRef } from 'react';

interface ScrollTypewriterProps {
  code: string;
  className?: string;
}

export default function ScrollTypewriter({ code, className = '' }: ScrollTypewriterProps) {
  const [displayedCode, setDisplayedCode] = useState('');
  const [isVisible, setIsVisible] = useState(false);
  const containerRef = useRef<HTMLPreElement>(null);
  const scrollProgress = useRef(0);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          setIsVisible(entry.isIntersecting);
        });
      },
      { threshold: 0.1 }
    );

    observer.observe(container);

    const handleScroll = () => {
      if (!container || !isVisible) return;

      const rect = container.getBoundingClientRect();
      const windowHeight = window.innerHeight;
      
      // Calculate scroll progress when element is in view
      const elementTop = rect.top;
      const elementHeight = rect.height;
      
      // Start typing when element enters viewport, complete when it's 70% through
      const startPoint = windowHeight;
      const endPoint = windowHeight * 0.3;
      
      if (elementTop <= startPoint && elementTop >= endPoint) {
        const progress = (startPoint - elementTop) / (startPoint - endPoint);
        scrollProgress.current = Math.min(Math.max(progress, 0), 1);
        
        const targetLength = Math.floor(code.length * scrollProgress.current);
        setDisplayedCode(code.substring(0, targetLength));
      } else if (elementTop < endPoint) {
        // Fully visible
        setDisplayedCode(code);
      } else {
        // Not yet visible
        setDisplayedCode('');
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Initial check

    return () => {
      observer.disconnect();
      window.removeEventListener('scroll', handleScroll);
    };
  }, [code, isVisible]);

  return (
    <pre ref={containerRef} className={className}>
      {displayedCode}
      {displayedCode.length < code.length && (
        <span className="animate-pulse text-green-400">|</span>
      )}
    </pre>
  );
}