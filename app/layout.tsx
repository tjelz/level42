import type { Metadata } from "next";
import { Inter, Orbitron, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const orbitron = Orbitron({
  variable: "--font-orbitron",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Level42 | Autonomous AI Agents That Pay",
  description: "Revolutionary framework enabling AI agents to autonomously pay for tools, APIs, and services using blockchain micropayments. No API keys. No subscriptions. Pure autonomy.",
  keywords: ["AI", "blockchain", "micropayments", "autonomous agents", "level42", "L42", "USDC", "Base Network"],
  authors: [{ name: "Level42 Team" }],
  creator: "Level42",
  publisher: "Level42",
  openGraph: {
    title: "Level42 | Autonomous AI Agents That Pay",
    description: "Revolutionary framework enabling AI agents to autonomously pay for tools, APIs, and services using blockchain micropayments.",
    url: "https://level42.dev",
    siteName: "Level42",
    images: [
      {
        url: "/l42-banner.jpeg",
        width: 1200,
        height: 630,
        alt: "Level42 - Autonomous AI Agents That Pay",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Level42 | Autonomous AI Agents That Pay",
    description: "Revolutionary framework enabling AI agents to autonomously pay for tools, APIs, and services using blockchain micropayments.",
    creator: "@level42ai",
    images: ["/l42-banner.jpeg"],
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
        <link rel="icon" href="/favicon.jpg" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <meta name="theme-color" content="#000000" />
        <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no, viewport-fit=cover" />
      </head>
      <body
        className={`${inter.variable} ${orbitron.variable} ${jetbrainsMono.variable} antialiased bg-black text-white`}
      >
        {children}
      </body>
    </html>
  );
}
