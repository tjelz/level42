'use client';

import { useState, useEffect } from 'react';

import LaserFlow from './components/LaserFlow';
import ElectricBorder from './components/ElectricBorder';
import GlowText from './components/GlowText';
import ScrollTypewriter from './components/ScrollTypewriter';
import React from 'react';

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [showNav, setShowNav] = useState(false);

  useEffect(() => {
    setMounted(true);

    const handleScroll = () => {
      const scrollY = window.scrollY;
      setShowNav(scrollY > 100);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden" style={{ overscrollBehavior: 'none', WebkitOverflowScrolling: 'touch' }}>
      {/* Animated Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-blue-900/20 to-cyan-900/20"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(120,119,198,0.1),transparent_50%)]"></div>
        <div className="grid-background"></div>
      </div>

      {/* Navigation - Floating Glass Pill */}
      {/* Minimal Floating Navigation */}
      <nav className={`fixed top-8 right-8 z-[100] transition-all duration-500 ${showNav
        ? 'opacity-100 translate-y-0'
        : 'opacity-0 -translate-y-4 pointer-events-none'
        }`}>
        <div className="flex items-center space-x-4">
          <a href="https://github.com/tjelz/level42"
            className="w-18 h-18 bg-[#1f1f1f] backdrop-blur-xl border border-white/10 rounded-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 hover:bg-black/80 hover:border-white/20 shadow-2xl magnetic-hover glow-on-hover"
            title="GitHub">
            <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
          </a>
          <a href="https://x.com/xlevel42"
            className="w-18 h-18 bg-[#1f1f1f] backdrop-blur-xl border border-white/10 rounded-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 hover:bg-black/80 hover:border-white/20 shadow-2xl magnetic-hover glow-on-hover"
            title="Twitter">
            <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
            </svg>
          </a>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen">
        {/* Laser Flow Animation - Full Screen */}
        <div className="absolute inset-0 overflow-hidden">
          <LaserFlow
            color="#a855f7"
            wispDensity={1.2}
            mouseTiltStrength={0.02}
            horizontalBeamOffset={0.0}
            verticalBeamOffset={0}
            flowSpeed={0.4}
            verticalSizing={2.2}
            horizontalSizing={0.8}
            fogIntensity={0.8}
            fogScale={0.25}
            wispSpeed={12.0}
            wispIntensity={6.0}
            flowStrength={0.3}
            decay={1.2}
            falloffStart={1.0}
            fogFallSpeed={0.8}
          />
        </div>

        {/* Floating particles */}
        <div className="floating-particles"></div>

        {/* Glass Container Box - Positioned at bottom */}
        <div className="absolute left-6 right-6 z-20 top-[50vh] md:top-[50vh] lg:top-[50vh]">
          <div className="max-w-6xl mx-auto">
            <div className="bg-black/20 backdrop-blur-sm border-2 border-purple-400/30 rounded-3xl p-12 shadow-2xl glow-on-hover border-pulse">
              <div className="text-center animate-fade-in">
                {/* Main Title */}
                <h1 className="text-5xl md:text-7xl font-display mb-8 leading-tight">
                  <GlowText className="text-5xl md:text-7xl font-display block text-shimmer mb-6">
                    level42
                  </GlowText>
                  <GlowText className="text-3xl md:text-5xl font-display block mt-2 text-shimmer">
                    Agents That Pay
                  </GlowText>
                </h1>

                {/* Description */}
                <div className="max-w-3xl mx-auto mb-10">
                  <p className="text-lg md:text-xl text-white/90 mb-3 leading-relaxed font-medium">
                    AI agents that pay for APIs automatically.
                  </p>
                  <p className="text-base md:text-lg text-cyan-300 font-bold">
                    No API keys. Pure autonomy.
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-col md:flex-row items-center justify-center space-y-4 md:space-y-0 md:space-x-6">
                  <a href="https://github.com/tjelz/level42" className="group px-10 py-4 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-xl text-lg font-black hover:scale-105 transition-all duration-300 shadow-xl border border-white/20 hover:border-white/40">
                    <span className="relative z-10 text-white">GitHub</span>
                  </a>
                  <a href="https://github.com/tjelz/level42/tree/main/docs" className="px-10 py-4 border-2 border-purple-400/60 rounded-xl text-lg font-black hover:bg-purple-500/20 hover:border-purple-300 transition-all duration-300 backdrop-blur-xl bg-black/40 shadow-xl text-white">
                    View Docs
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      {/* Features Section */}
      <section className="relative z-10 py-20 px-6">
        {/* Background pattern */}
        <div className="absolute inset-0 pattern-dots opacity-30"></div>

        <div className="max-w-7xl mx-auto relative">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-6xl font-display mb-6">
              <GlowText className="text-4xl md:text-6xl font-display text-shimmer">
                Revolutionary Architecture
              </GlowText>
            </h2>
            <p className="text-xl text-gray-400 max-w-4xl mx-auto leading-relaxed">
              Breakthrough technology that eliminates API friction through autonomous blockchain micropayments.
              <span className="text-white font-semibold"> No more API keys, subscriptions, or manual integrations.</span>
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                title: "Autonomous Micropayments",
                description: "Agents automatically pay for API access using USDC without human intervention",
                icon: (
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1L9 7V9C9 10.1 9.9 11 11 11V22H13V11C14.1 11 15 10.1 15 9H21Z" />
                    <circle cx="12" cy="16" r="2" />
                    <path d="M7 18C7 16.9 7.9 16 9 16H15C16.1 16 17 16.9 17 18V20H7V18Z" />
                  </svg>
                ),
                color: "#a855f7"
              },
              {
                title: "HTTP 402 Integration",
                description: "Seamless handling of payment-required responses across any API",
                icon: (
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                    <rect x="2" y="4" width="20" height="16" rx="2" ry="2" />
                    <path d="M7 15H17M7 11H17" />
                    <rect x="5" y="7" width="4" height="2" />
                  </svg>
                ),
                color: "#06b6d4"
              },
              {
                title: "Multi-Agent Swarms",
                description: "Collaborative agents with intelligent cost-splitting capabilities",
                icon: (
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                    <circle cx="9" cy="7" r="4" />
                    <path d="M3 21V19C3 16.79 4.79 15 7 15H11C13.21 15 15 16.79 15 19V21" />
                    <circle cx="16" cy="11" r="3" />
                    <path d="M22 21V20C22 18.35 20.65 17 19 17C18.5 17 18.03 17.12 17.62 17.35" />
                  </svg>
                ),
                color: "#ec4899"
              },
              {
                title: "Deferred Payment Batching",
                description: "Efficient transaction batching to minimize gas costs and maximize throughput",
                icon: (
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                    <rect x="3" y="4" width="18" height="4" rx="1" />
                    <rect x="3" y="10" width="18" height="4" rx="1" />
                    <rect x="3" y="16" width="18" height="4" rx="1" />
                  </svg>
                ),
                color: "#ffffffff"
              },
              {
                title: "Multi-Blockchain Support",
                description: "Base Network primary with extensible support for Solana and Ethereum",
                icon: (
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="3" />
                    <circle cx="12" cy="5" r="2" />
                    <circle cx="19" cy="9" r="2" />
                    <circle cx="19" cy="15" r="2" />
                    <circle cx="12" cy="19" r="2" />
                    <circle cx="5" cy="15" r="2" />
                    <circle cx="5" cy="9" r="2" />
                    <path d="M12 8V10M15.5 10.5L14.5 11.5M15.5 13.5L14.5 12.5M12 14V16M8.5 13.5L9.5 12.5M8.5 10.5L9.5 11.5" />
                  </svg>
                ),
                color: "#10b981"
              },
              {
                title: "Secure Wallet Management",
                description: "Non-persistent private key handling with enterprise-grade security",
                icon: (
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                    <rect x="3" y="11" width="18" height="10" rx="2" ry="2" />
                    <circle cx="12" cy="16" r="1" />
                    <path d="M7 11V7C7 4.24 9.24 2 12 2S17 4.24 17 7V11" />
                  </svg>
                ),
                color: "#f59e0b"
              }
            ].map((feature, index) => (
              <ElectricBorder
                key={index}
                color={feature.color}
                speed={0.8}
                chaos={0.6}
                thickness={2}
                style={{ borderRadius: 20 }}
                className="group hover:scale-105 transition-all duration-300 magnetic-hover"
              >
                <div className="relative bg-gradient-to-br from-gray-900/90 via-gray-800/80 to-gray-900/90 backdrop-blur-xl rounded-[20px] border border-white/5 shadow-2xl overflow-hidden glow-on-hover">
                  {/* Icon Header Section */}
                  <div className="relative h-32 bg-gradient-to-br from-gray-800/90 to-gray-900/90 flex items-center justify-center overflow-hidden">
                    {/* Header background pattern */}
                    <div className="absolute inset-0 bg-gradient-to-br from-white/[0.03] via-transparent to-black/30"></div>

                    {/* Large background icon - cut off and blended */}
                    <div className="absolute inset-0 flex items-center justify-center opacity-8 scale-150 group-hover:scale-160 transition-transform duration-500"
                      style={{ color: `${feature.color}40` }}>
                      <div className="w-24 h-24">
                        {React.cloneElement(feature.icon as React.ReactElement<any>, {
                          className: "w-full h-full"
                        })}
                      </div>
                    </div>

                    {/* Foreground icon */}
                    <div className="relative z-10 w-12 h-12 group-hover:scale-110 transition-all duration-300"
                      style={{
                        color: feature.color,
                        filter: `drop-shadow(0 0 12px ${feature.color}60)`
                      }}>
                      {React.cloneElement(feature.icon as React.ReactElement<any>, {
                        className: "w-full h-full"
                      })}
                    </div>

                    {/* Header gradient overlay */}
                    <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-gray-900/90 to-transparent"></div>
                  </div>

                  {/* Content Section */}
                  <div className="relative p-6">
                    {/* Metal texture overlay */}
                    <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] via-transparent to-black/20 pointer-events-none"></div>

                    <div className="relative z-10">
                      <h3 className="text-xl font-display font-bold mb-4 text-white group-hover:text-white transition-colors duration-300 glitch-effect">
                        {feature.title}
                      </h3>
                      <p className="text-gray-400 leading-relaxed text-sm group-hover:text-gray-300 transition-colors duration-300">
                        {feature.description}
                      </p>
                    </div>
                  </div>

                  {/* Subtle highlight line */}
                  <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
                </div>
              </ElectricBorder>
            ))}
          </div>
        </div>
      </section>

      {/* Code Example Section */}
      <section className="relative z-10 py-20 px-6">
        {/* Floating particles for this section */}
        <div className="floating-particles"></div>

        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-6xl font-display mb-6">
              <GlowText className="text-4xl md:text-6xl font-display text-shimmer">
                Developer Experience
              </GlowText>
            </h2>
            <p className="text-xl text-gray-400 max-w-4xl mx-auto leading-relaxed">
              Deploy autonomous payment-enabled agents in minutes, not months.
              <span className="text-white font-semibold"> One framework, infinite possibilities.</span>
            </p>
          </div>

          <div className="bg-gray-900/80 rounded-2xl p-8 border border-gray-700/50 backdrop-blur-sm glow-on-hover border-pulse">
            <div className="flex items-center justify-between mb-6">
              <div className="flex space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              </div>
              <span className="text-gray-400 text-sm font-mono">main.py</span>
            </div>
            <ScrollTypewriter
              className="text-green-400 text-sm md:text-base overflow-x-auto font-mono"
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
      </section>

      {/* The Future is Autonomous */}
      <section className="relative z-10 py-40 px-6 overflow-hidden">
        {/* Dramatic background effects */}
        <div className="absolute inset-0 bg-gradient-to-b from-black via-purple-900/20 to-black"></div>
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(168,85,247,0.15),transparent_60%)]"></div>

        {/* Animated grid overlay */}
        <div className="absolute inset-0 opacity-20">
          <div className="grid-background"></div>
        </div>

        <div className="max-w-6xl mx-auto relative z-10 text-center">
          {/* Dramatic headline */}
          <div className="mb-20">
            <GlowText className="text-6xl md:text-8xl font-display mb-8 leading-tight text-shimmer breathe-animation">
              The Last API Key
            </GlowText>
            <br />
            <GlowText className="text-6xl md:text-8xl font-display mb-12 leading-tight text-shimmer breathe-animation">
              You'll Ever Need
            </GlowText>
          </div>

          {/* Call to Action */}
          <div className="max-w-4xl mx-auto">
            <div className="relative ">

              <div className="relative z-10 p-16 text-center">
                <GlowText className="text-5xl md:text-6xl font-display mb-12 glitch-effect typewriter-cursor">
                  L42 CA COMING SOON
                </GlowText>

              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}