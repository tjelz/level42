'use client';

import { useEffect, useState } from 'react';

interface PerformanceStats {
  fps: number;
  memoryUsage: number;
  renderTime: number;
}

export default function PerformanceMonitor() {
  const [stats, setStats] = useState<PerformanceStats>({
    fps: 0,
    memoryUsage: 0,
    renderTime: 0
  });
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    let frameCount = 0;
    let lastTime = performance.now();
    let animationId: number;

    const measurePerformance = () => {
      frameCount++;
      const currentTime = performance.now();
      
      if (currentTime - lastTime >= 1000) {
        const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
        
        // Memory usage (if available)
        const memory = (performance as any).memory;
        const memoryUsage = memory ? Math.round(memory.usedJSHeapSize / 1048576) : 0;
        
        setStats({
          fps,
          memoryUsage,
          renderTime: Math.round(currentTime - lastTime)
        });
        
        frameCount = 0;
        lastTime = currentTime;
      }
      
      animationId = requestAnimationFrame(measurePerformance);
    };

    if (isVisible) {
      measurePerformance();
    }

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, [isVisible]);

  // Toggle visibility with keyboard shortcut
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'P') {
        setIsVisible(!isVisible);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <div className="fixed top-4 left-4 z-[9999] bg-black/80 backdrop-blur-sm border border-white/20 rounded-lg p-3 text-xs font-mono text-white">
      <div className="mb-1">Performance Monitor</div>
      <div className={`${stats.fps >= 30 ? 'text-green-400' : stats.fps >= 20 ? 'text-yellow-400' : 'text-red-400'}`}>
        FPS: {stats.fps}
      </div>
      {stats.memoryUsage > 0 && (
        <div className={`${stats.memoryUsage < 100 ? 'text-green-400' : stats.memoryUsage < 200 ? 'text-yellow-400' : 'text-red-400'}`}>
          Memory: {stats.memoryUsage}MB
        </div>
      )}
      <div className="text-gray-400 text-[10px] mt-1">
        Ctrl+Shift+P to toggle
      </div>
    </div>
  );
}