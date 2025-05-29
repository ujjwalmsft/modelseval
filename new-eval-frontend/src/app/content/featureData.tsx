/**
 * Feature data configuration for the application's features showcase.
 * 
 * Defines content for interactive feature cards with consistent formatting.
 * Includes Material UI icons for visual representation of each feature.
 * Provides descriptive text explaining key benefits of the comparison tool.
 * Structures data for easy consumption by feature display components.
 * Implements typed interface for robust feature item structure validation.
 */

import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import PsychologyIcon from '@mui/icons-material/Psychology';
import SpeedIcon from '@mui/icons-material/Speed';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import { ReactNode } from 'react';

interface FeatureItem {
  icon: ReactNode;
  title: string;
  description: string;
}

export const featureData: FeatureItem[] = [
  {
    icon: <CompareArrowsIcon sx={{ fontSize: 40 }} />,
    title: "Side-by-Side Comparison",
    description: "Compare responses from multiple leading language models with the same prompt. Easily see differences in reasoning, style and accuracy."
  },
  {
    icon: <PsychologyIcon sx={{ fontSize: 40 }} />,
    title: "Understand Model Strengths",
    description: "Identify which models excel at specific tasks such as creative writing, reasoning, code generation, or factual responses."
  },
  {
    icon: <SpeedIcon sx={{ fontSize: 40 }} />,
    title: "Performance Metrics",
    description: "Track response times, token usage, and other performance metrics to optimize your AI implementation for efficiency."
  },
  {
    icon: <AnalyticsIcon sx={{ fontSize: 40 }} />,
    title: "Save & Analyze History",
    description: "Build a library of comparisons that you can review later, helping you track model improvements over time."
  }
];