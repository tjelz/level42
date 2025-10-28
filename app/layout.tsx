import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "x402-Agent | Autonomous AI Agents That Pay",
  description: "Revolutionary framework enabling AI agents to autonomously pay for tools, APIs, and services using blockchain micropayments. No API keys. No subscriptions. Pure autonomy.",
  keywords: ["AI", "blockchain", "micropayments", "autonomous agents", "x402", "USDC", "Base Network"],
  authors: [{ name: "x402-Agent Team" }],
  creator: "x402-Agent",
  publisher: "x402-Agent",
  openGraph: {
    title: "x402-Agent | Autonomous AI Agents That Pay",
    description: "Revolutionary framework enabling AI agents to autonomously pay for tools, APIs, and services using blockchain micropayments.",
    url: "https://x402-agent.dev",
    siteName: "x402-Agent",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "x402-Agent - Autonomous AI Agents That Pay",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "x402-Agent | Autonomous AI Agents That Pay",
    description: "Revolutionary framework enabling AI agents to autonomously pay for tools, APIs, and services using blockchain micropayments.",
    creator: "@x402agent",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <meta name="theme-color" content="#000000" />
        <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no, viewport-fit=cover" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-black text-white`}
      >
        {children}
      </body>
    </html>
  );
}
