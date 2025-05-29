/**
 * Theme configuration for Material UI components.
 * 
 * Provides centralized theme creation with light/dark mode variants.
 * Defines consistent color palettes with proper contrast for accessibility.
 * Implements utility functions for gradient text and background styles.
 * Maintains typography settings with fallback font stacks.
 */

import { createTheme } from '@mui/material/styles';
import { PaletteMode } from '@mui/material';

export const createAppTheme = (mode: PaletteMode) => {
  return createTheme({
    palette: {
      mode,
      primary: {
        main: mode === 'light' ? '#1976d2' : '#90caf9',
      },
      secondary: {
        main: mode === 'light' ? '#9c27b0' : '#ce93d8',
      },
    },
    typography: {
      fontFamily: '"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    },
  });
};

export const getGradientText = (mode: PaletteMode) => {
  return mode === 'dark'
    ? 'linear-gradient(90deg, #60a5fa, #a78bfa)'
    : 'linear-gradient(90deg, #3b82f6, #8b5cf6)';
};

export const getBackgroundGradient = (mode: PaletteMode) => {
  return mode === 'dark'
    ? 'linear-gradient(135deg, rgba(13,17,23,0.9) 0%, rgba(20,29,47,0.9) 100%)'
    : 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,242,245,0.9) 100%)';
};