/**
 * Root layout component providing global application structure.
 * 
 * Configures font loading with Geist Sans and Geist Mono for consistent typography.
 * Wraps the application in the AuthProvider for authentication state management.
 */

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ModelProvider } from './context/ModelContext';
import { AuthProvider } from './auth/authContext';
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: 'Model Comparison',
  description: 'Compare outputs from different LLM models',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
         <AuthProvider>
         <ModelProvider>
             {children}
           </ModelProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
