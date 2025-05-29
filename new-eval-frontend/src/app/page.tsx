/**
 * Main landing page component for the LLM comparison application.
 * 
 * Provides the application's entry point with responsive theme management.
 * Features a hero section with prominent call-to-action for user engagement.
 * Implements smooth scrolling navigation to the features section.
 * Uses Material UI theming with light/dark mode toggle based on system preferences.
 * Renders the application's main sections in a cohesive, structured layout.
 */

'use client';

import { useState, useEffect, useMemo, useRef } from 'react';
import { Box, CssBaseline, ThemeProvider, useMediaQuery } from '@mui/material';
import { useRouter } from 'next/navigation';
import { useAuth } from './auth/authContext';
import { createAppTheme } from '../../theme/theme';

// Import components
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import FeaturesSection from './components/FeaturesSection';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const featuresRef = useRef<HTMLDivElement>(null);
  
  // Use system preference as default theme
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  const [mode, setMode] = useState<'light' | 'dark'>(prefersDarkMode ? 'dark' : 'light');

  // Create theme with current mode
  const theme = useMemo(() => createAppTheme(mode), [mode]);

  // Function to handle smooth scrolling
  const scrollToFeatures = () => {
    featuresRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });
  };

// to clear previous selections when returning to home page:
useEffect(() => {
  // When the home page is loaded, we don't need to clear localStorage
  // This allows users to navigate back and forth while maintaining their selection
  
  // However, to start fresh each time a user visits the home page:
  // localStorage.removeItem('selectedModels');
}, []);

  // Toggle theme mode
  const toggleColorMode = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box>
        <Header mode={mode} toggleColorMode={toggleColorMode} />
        <HeroSection mode={mode} scrollToFeatures={scrollToFeatures} />
        <FeaturesSection mode={mode} featuresSectionRef={featuresRef} />
      </Box>
    </ThemeProvider>
  );
}