'use client';

import { useState, useEffect } from 'react';
import ScrollTypewriter from './components/ScrollTypewriter';
import PerformanceMonitor from './components/PerformanceMonitor';

interface WindowState {
  id: string;
  title: string;
  icon: string;
  isOpen: boolean;
  isMinimized: boolean;
  isMaximized: boolean;
  position: { x: number; y: number };
  size: { width: number; height: number };
  zIndex: number;
}

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [windows, setWindows] = useState<WindowState[]>([
    {
      id: 'about',
      title: 'About level42',
      icon: '📁',
      isOpen: false,
      isMinimized: false,
      isMaximized: false,
      position: { x: 100, y: 100 },
      size: { width: 600, height: 400 },
      zIndex: 1
    },
    {
      id: 'features',
      title: 'Features',
      icon: '⚙️',
      isOpen: false,
      isMinimized: false,
      isMaximized: false,
      position: { x: 150, y: 150 },
      size: { width: 700, height: 500 },
      zIndex: 1
    },
    {
      id: 'code',
      title: 'Code Example - Notepad',
      icon: '📝',
      isOpen: false,
      isMinimized: false,
      isMaximized: false,
      position: { x: 200, y: 200 },
      size: { width: 800, height: 600 },
      zIndex: 1
    },
    {
      id: 'info',
      title: 'level42 - Information',
      icon: 'ℹ️',
      isOpen: false,
      isMinimized: false,
      isMaximized: false,
      position: { x: 250, y: 250 },
      size: { width: 500, height: 350 },
      zIndex: 1
    }
  ]);
  const [dragState, setDragState] = useState<{
    isDragging: boolean;
    windowId: string | null;
    offset: { x: number; y: number };
  }>({
    isDragging: false,
    windowId: null,
    offset: { x: 0, y: 0 }
  });
  const [highestZIndex, setHighestZIndex] = useState(1);
  const [showWelcome, setShowWelcome] = useState(true);
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; show: boolean }>({
    x: 0,
    y: 0,
    show: false
  });

  useEffect(() => {
    setMounted(true);

    // Update time every second for XP taskbar
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    // Auto-hide welcome message after 3 seconds
    const welcomeTimer = setTimeout(() => {
      setShowWelcome(false);
    }, 3000);

    return () => {
      clearInterval(timer);
      clearTimeout(welcomeTimer);
    };
  }, []);

  const openWindow = (windowId: string) => {
    // Simulate XP window opening sound
    console.log('🔊 Window opening sound');
    
    setWindows(prev => prev.map(w => 
      w.id === windowId 
        ? { ...w, isOpen: true, isMinimized: false, zIndex: highestZIndex + 1 }
        : w
    ));
    setHighestZIndex(prev => prev + 1);
  };

  const closeWindow = (windowId: string) => {
    // Simulate XP window closing sound
    console.log('🔊 Window closing sound');
    
    setWindows(prev => prev.map(w => 
      w.id === windowId ? { ...w, isOpen: false, isMinimized: false } : w
    ));
  };

  const minimizeWindow = (windowId: string) => {
    setWindows(prev => prev.map(w => 
      w.id === windowId ? { ...w, isMinimized: true } : w
    ));
  };

  const maximizeWindow = (windowId: string) => {
    setWindows(prev => prev.map(w => 
      w.id === windowId 
        ? { 
            ...w, 
            isMaximized: !w.isMaximized,
            position: w.isMaximized ? w.position : { x: 0, y: 0 },
            size: w.isMaximized ? w.size : { width: window.innerWidth, height: window.innerHeight - 40 }
          }
        : w
    ));
  };

  const focusWindow = (windowId: string) => {
    setWindows(prev => prev.map(w => 
      w.id === windowId ? { ...w, zIndex: highestZIndex + 1, isMinimized: false } : w
    ));
    setHighestZIndex(prev => prev + 1);
  };

  const handleMouseDown = (e: React.MouseEvent, windowId: string) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setDragState({
      isDragging: true,
      windowId,
      offset: {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      }
    });
    focusWindow(windowId);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (dragState.isDragging && dragState.windowId) {
      const newX = e.clientX - dragState.offset.x;
      const newY = e.clientY - dragState.offset.y;
      
      setWindows(prev => prev.map(w => 
        w.id === dragState.windowId 
          ? { ...w, position: { x: Math.max(0, newX), y: Math.max(0, newY) } }
          : w
      ));
    }
  };

  const handleMouseUp = () => {
    setDragState({
      isDragging: false,
      windowId: null,
      offset: { x: 0, y: 0 }
    });
  };

  const handleRightClick = (e: React.MouseEvent) => {
    e.preventDefault();
    setContextMenu({
      x: e.clientX,
      y: e.clientY,
      show: true
    });
  };

  const hideContextMenu = () => {
    setContextMenu(prev => ({ ...prev, show: false }));
  };

  if (!mounted) return null;

  return (
    <div 
      className="h-screen bg-gradient-to-b from-blue-400 via-blue-500 to-blue-600 text-black overflow-hidden select-none" 
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onContextMenu={handleRightClick}
      onClick={hideContextMenu}
      style={{ overscrollBehavior: 'none', WebkitOverflowScrolling: 'touch' }}
    >
      <PerformanceMonitor />
      
      {/* Windows XP Desktop Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-400 via-blue-500 to-blue-600"></div>
        {/* XP-style clouds */}
        <div className="absolute inset-0 opacity-40">
          <div className="absolute top-20 left-20 w-32 h-16 bg-white/30 rounded-full"></div>
          <div className="absolute top-32 right-40 w-24 h-12 bg-white/20 rounded-full"></div>
          <div className="absolute top-16 right-20 w-20 h-10 bg-white/25 rounded-full"></div>
        </div>
      </div>

      {/* Welcome Message */}
      {showWelcome && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 bg-gradient-to-b from-gray-100 to-gray-200 border-2 border-gray-600 rounded-lg shadow-2xl overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-blue-800 px-4 py-2 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-b from-yellow-300 to-yellow-500 border border-yellow-200 rounded-sm flex items-center justify-center">
                <span className="text-xs">🏠</span>
              </div>
              <span className="text-white font-bold text-sm">Welcome to level42 Desktop</span>
            </div>
            <button 
              className="w-6 h-6 bg-gradient-to-b from-red-400 to-red-600 border border-red-300 rounded-sm hover:from-red-300 hover:to-red-500 flex items-center justify-center text-white text-xs font-bold"
              onClick={() => setShowWelcome(false)}
            >
              ×
            </button>
          </div>
          <div className="p-6 text-center">
            <div className="flex items-center justify-center mb-4">
              <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white text-2xl mr-4">
                👋
              </div>
              <div className="text-left">
                <h3 className="text-lg font-bold text-blue-900">Welcome!</h3>
                <p className="text-sm text-gray-700">Double-click icons to open applications</p>
              </div>
            </div>
            <button 
              className="px-6 py-2 bg-gradient-to-b from-blue-400 to-blue-600 border-2 border-blue-300 rounded text-white font-bold hover:from-blue-300 hover:to-blue-500 transition-all duration-150 shadow-lg"
              onClick={() => setShowWelcome(false)}
            >
              OK
            </button>
          </div>
        </div>
      )}

      {/* Desktop Icons */}
      <div className="absolute top-8 left-8 z-20 space-y-6">
        <div 
          className="flex flex-col items-center space-y-1 cursor-pointer hover:bg-blue-400/20 p-2 rounded"
          onDoubleClick={() => openWindow('about')}
        >
          <div className="w-12 h-12 bg-gradient-to-b from-yellow-300 to-yellow-500 border-2 border-yellow-200 rounded-lg shadow-lg flex items-center justify-center">
            <span className="text-2xl">📁</span>
          </div>
          <span className="text-white text-xs font-bold drop-shadow-lg">About level42</span>
        </div>
        
        <div 
          className="flex flex-col items-center space-y-1 cursor-pointer hover:bg-blue-400/20 p-2 rounded"
          onDoubleClick={() => openWindow('features')}
        >
          <div className="w-12 h-12 bg-gradient-to-b from-blue-300 to-blue-500 border-2 border-blue-200 rounded-lg shadow-lg flex items-center justify-center">
            <span className="text-2xl">⚙️</span>
          </div>
          <span className="text-white text-xs font-bold drop-shadow-lg">Features</span>
        </div>
        
        <div 
          className="flex flex-col items-center space-y-1 cursor-pointer hover:bg-blue-400/20 p-2 rounded"
          onDoubleClick={() => openWindow('code')}
        >
          <div className="w-12 h-12 bg-gradient-to-b from-white to-gray-200 border-2 border-gray-300 rounded-lg shadow-lg flex items-center justify-center">
            <span className="text-2xl">📝</span>
          </div>
          <span className="text-white text-xs font-bold drop-shadow-lg">Code Example</span>
        </div>
        
        <div 
          className="flex flex-col items-center space-y-1 cursor-pointer hover:bg-blue-400/20 p-2 rounded"
          onDoubleClick={() => openWindow('info')}
        >
          <div className="w-12 h-12 bg-gradient-to-b from-blue-400 to-blue-600 border-2 border-blue-300 rounded-lg shadow-lg flex items-center justify-center">
            <span className="text-2xl">ℹ️</span>
          </div>
          <span className="text-white text-xs font-bold drop-shadow-lg">Information</span>
        </div>
        
        <div className="flex flex-col items-center space-y-1 cursor-pointer hover:bg-blue-400/20 p-2 rounded">
          <div className="w-12 h-12 bg-gradient-to-b from-gray-300 to-gray-500 border-2 border-gray-200 rounded-lg shadow-lg flex items-center justify-center">
            <span className="text-2xl">🗑️</span>
          </div>
          <span className="text-white text-xs font-bold drop-shadow-lg">Recycle Bin</span>
        </div>
      </div>

      {/* Windows */}
      {windows.map(window => (
        window.isOpen && !window.isMinimized && (
          <div
            key={window.id}
            className="absolute bg-gradient-to-b from-gray-100 to-gray-200 border-2 border-gray-600 rounded-lg shadow-2xl overflow-hidden window-opening"
            style={{
              left: window.position.x,
              top: window.position.y,
              width: window.size.width,
              height: window.size.height,
              zIndex: window.zIndex
            }}
            onClick={() => focusWindow(window.id)}
          >
            {/* Window Title Bar */}
            <div 
              className="bg-gradient-to-r from-blue-600 to-blue-800 px-4 py-2 flex items-center justify-between cursor-move"
              onMouseDown={(e) => handleMouseDown(e, window.id)}
            >
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-gradient-to-b from-yellow-300 to-yellow-500 border border-yellow-200 rounded-sm flex items-center justify-center">
                  <span className="text-xs">{window.icon}</span>
                </div>
                <span className="text-white font-bold text-sm">{window.title}</span>
              </div>
              <div className="flex items-center space-x-1">
                <button 
                  className="w-6 h-6 bg-gradient-to-b from-gray-300 to-gray-500 border border-gray-400 rounded-sm hover:from-gray-200 hover:to-gray-400 flex items-center justify-center text-xs font-bold"
                  onClick={(e) => { e.stopPropagation(); minimizeWindow(window.id); }}
                >
                  _
                </button>
                <button 
                  className="w-6 h-6 bg-gradient-to-b from-gray-300 to-gray-500 border border-gray-400 rounded-sm hover:from-gray-200 hover:to-gray-400 flex items-center justify-center text-xs font-bold"
                  onClick={(e) => { e.stopPropagation(); maximizeWindow(window.id); }}
                >
                  □
                </button>
                <button 
                  className="w-6 h-6 bg-gradient-to-b from-red-400 to-red-600 border border-red-300 rounded-sm hover:from-red-300 hover:to-red-500 flex items-center justify-center text-white text-xs font-bold"
                  onClick={(e) => { e.stopPropagation(); closeWindow(window.id); }}
                >
                  ×
                </button>
              </div>
            </div>
            
            {/* Window Content */}
            <div className="h-full overflow-auto">
              {window.id === 'about' && (
                <div className="p-8 text-center">
                  <h1 className="text-4xl md:text-6xl font-bold mb-6 text-blue-900">level42</h1>
                  <h2 className="text-2xl md:text-4xl font-bold mb-8 text-blue-700">Agents That Pay</h2>
                  <div className="max-w-2xl mx-auto mb-8">
                    <p className="text-lg text-gray-700 mb-3 leading-relaxed">
                      AI agents that pay for APIs automatically.
                    </p>
                    <p className="text-base text-blue-600 font-bold">
                      No API keys. Pure autonomy.
                    </p>
                  </div>
                  <div className="flex flex-col md:flex-row items-center justify-center space-y-4 md:space-y-0 md:space-x-6">
                    <a href="https://github.com/tjelz/level42" className="px-8 py-3 bg-gradient-to-b from-blue-400 to-blue-600 border-2 border-blue-300 rounded text-white font-bold hover:from-blue-300 hover:to-blue-500 transition-all duration-150 shadow-lg">
                      View on GitHub
                    </a>
                    <a href="https://github.com/tjelz/level42/tree/main/docs" className="px-8 py-3 bg-gradient-to-b from-gray-200 to-gray-400 border-2 border-gray-300 rounded text-gray-800 font-bold hover:from-gray-100 hover:to-gray-300 transition-all duration-150 shadow-lg">
                      Read Documentation
                    </a>
                  </div>
                </div>
              )}
              
              {window.id === 'features' && (
                <div className="p-6">
                  <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold mb-4 text-blue-900">Revolutionary Architecture</h2>
                    <p className="text-sm text-gray-700 leading-relaxed">
                      Breakthrough technology that eliminates API friction through autonomous blockchain micropayments.
                    </p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                      { title: "Autonomous Micropayments", description: "Agents automatically pay for API access using USDC without human intervention", icon: "💰" },
                      { title: "HTTP 402 Integration", description: "Seamless handling of payment-required responses across any API", icon: "🌐" },
                      { title: "Multi-Agent Swarms", description: "Collaborative agents with intelligent cost-splitting capabilities", icon: "👥" },
                      { title: "Deferred Payment Batching", description: "Efficient transaction batching to minimize gas costs and maximize throughput", icon: "📊" },
                      { title: "Multi-Blockchain Support", description: "Base Network primary with extensible support for Solana and Ethereum", icon: "🔗" },
                      { title: "Secure Wallet Management", description: "Non-persistent private key handling with enterprise-grade security", icon: "🔒" }
                    ].map((feature, index) => (
                      <div key={index} className="bg-white border border-gray-300 rounded p-4 shadow-sm">
                        <div className="text-2xl mb-2">{feature.icon}</div>
                        <h3 className="text-sm font-bold mb-2 text-blue-900">{feature.title}</h3>
                        <p className="text-xs text-gray-700 leading-relaxed">{feature.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {window.id === 'code' && (
                <div className="h-full flex flex-col">
                  {/* Menu Bar */}
                  <div className="bg-gray-200 border-b border-gray-400 px-2 py-1">
                    <div className="flex space-x-4 text-xs">
                      <span className="hover:bg-blue-200 px-2 py-1 cursor-pointer">File</span>
                      <span className="hover:bg-blue-200 px-2 py-1 cursor-pointer">Edit</span>
                      <span className="hover:bg-blue-200 px-2 py-1 cursor-pointer">Format</span>
                      <span className="hover:bg-blue-200 px-2 py-1 cursor-pointer">View</span>
                      <span className="hover:bg-blue-200 px-2 py-1 cursor-pointer">Help</span>
                    </div>
                  </div>
                  {/* Code Content */}
                  <div className="bg-white p-4 font-mono text-xs text-black flex-1 overflow-auto">
                    <ScrollTypewriter
                      className="text-black text-xs font-mono leading-relaxed"
                      code={`from level42 import Level42Agent
from langchain_openai import ChatOpenAI

# Initialize your LLM
llm = ChatOpenAI(model="gpt-4")

# Create an agent with your wallet
agent = Level42Agent(
    llm=llm, 
    wallet_key="your_base_network_private_key"
)

# Register a paid API tool
agent.register_tool(
    name="weather",
    endpoint="https://api.weather.com/v1/current",
    description="Get current weather data"
)

# Run a task - payments handled automatically
result = agent.run("Get the current weather in San Francisco")
print(result)`}
                    />
                  </div>
                </div>
              )}
              
              {window.id === 'info' && (
                <div className="p-6 text-center">
                  <div className="flex items-center justify-center mb-6">
                    <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white text-2xl mr-4">
                      ℹ️
                    </div>
                    <div className="text-left">
                      <h3 className="text-xl font-bold text-blue-900 mb-1">The Last API Key</h3>
                      <h4 className="text-lg font-bold text-blue-700">You'll Ever Need</h4>
                    </div>
                  </div>
                  <p className="text-gray-700 mb-6 leading-relaxed text-sm">
                    Revolutionary blockchain-powered agent framework launching soon. 
                    Join the waitlist to be among the first to experience truly autonomous AI.
                  </p>
                  <div className="text-center">
                    <div className="bg-yellow-100 border-2 border-yellow-400 rounded p-4 mb-4">
                      <p className="text-lg font-bold text-blue-900 mb-1">L42 CA COMING SOON</p>
                      <p className="text-xs text-gray-600">Stay tuned for the token launch</p>
                    </div>
                    <button className="px-6 py-2 bg-gradient-to-b from-blue-400 to-blue-600 border-2 border-blue-300 rounded text-white font-bold hover:from-blue-300 hover:to-blue-500 transition-all duration-150 shadow-lg">
                      OK
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )
      ))}

      {/* Right-click Context Menu */}
      {contextMenu.show && (
        <div 
          className="absolute bg-gray-100 border border-gray-400 shadow-lg rounded-sm z-[200] py-1"
          style={{ left: contextMenu.x, top: contextMenu.y }}
        >
          <div className="px-4 py-2 hover:bg-blue-200 cursor-pointer text-xs" onClick={() => { openWindow('about'); hideContextMenu(); }}>
            Open About level42
          </div>
          <div className="px-4 py-2 hover:bg-blue-200 cursor-pointer text-xs" onClick={() => { openWindow('features'); hideContextMenu(); }}>
            View Features
          </div>
          <div className="px-4 py-2 hover:bg-blue-200 cursor-pointer text-xs" onClick={() => { openWindow('code'); hideContextMenu(); }}>
            Code Example
          </div>
          <hr className="border-gray-300 my-1" />
          <div className="px-4 py-2 hover:bg-blue-200 cursor-pointer text-xs">
            Properties
          </div>
        </div>
      )}

      {/* Windows XP Taskbar */}
      <div className="fixed bottom-0 left-0 right-0 z-[100] h-10 bg-gradient-to-b from-blue-600 to-blue-800 border-t-2 border-blue-300 shadow-lg">
        <div className="flex items-center h-full px-2">
          {/* Start Button */}
          <button className="h-8 px-4 bg-gradient-to-b from-green-400 to-green-600 border border-green-300 rounded-sm shadow-md hover:from-green-300 hover:to-green-500 transition-all duration-150 flex items-center space-x-2 font-bold text-white text-sm">
            <div className="w-4 h-4 bg-red-500 rounded-full border border-red-300"></div>
            <span>start</span>
          </button>
          
          {/* Quick Launch */}
          <div className="flex items-center ml-2 space-x-1">
            <div className="w-px h-6 bg-blue-400"></div>
            <a href="https://github.com/tjelz/level42" className="w-8 h-8 bg-blue-500 border border-blue-300 rounded-sm hover:bg-blue-400 transition-colors flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
            </a>
            <a href="https://x.com/xlevel42" className="w-8 h-8 bg-blue-500 border border-blue-300 rounded-sm hover:bg-blue-400 transition-colors flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
              </svg>
            </a>
          </div>
          
          {/* Taskbar Buttons for Open Windows */}
          <div className="flex items-center ml-4 space-x-1">
            {windows.filter(w => w.isOpen).map(window => (
              <button
                key={window.id}
                className={`h-8 px-3 text-xs font-bold transition-all duration-150 flex items-center space-x-1 ${
                  window.isMinimized 
                    ? 'bg-gradient-to-b from-gray-300 to-gray-500 border border-gray-400 text-gray-800' 
                    : 'bg-gradient-to-b from-blue-300 to-blue-500 border border-blue-200 text-white'
                } rounded-sm shadow-sm hover:from-blue-200 hover:to-blue-400`}
                onClick={() => window.isMinimized ? focusWindow(window.id) : minimizeWindow(window.id)}
              >
                <span className="text-xs">{window.icon}</span>
                <span className="truncate max-w-24">{window.title}</span>
              </button>
            ))}
          </div>
          
          {/* System Tray */}
          <div className="ml-auto flex items-center space-x-2 text-white text-xs">
            <div className="flex items-center space-x-1">
              <div className="w-4 h-4 bg-yellow-400 rounded-sm border border-yellow-300"></div>
              <span>🔊</span>
            </div>
            <div className="w-px h-6 bg-blue-400"></div>
            <span className="font-mono">
              {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        </div>
      </div>


    </div>
  );
}