/**
 * Hero section component with animated introduction and call-to-action.
 * 
 * Provides an engaging landing area with gradient text and background effects.
 * Features authentication state-aware buttons for user sign-in or navigation.
 * Implements responsive layout with two-column design on larger screens.
 * Uses Framer Motion for scroll indicator and text entrance animations.
 * Includes themed styling with automatic light/dark mode adaptation.
 */

'use client';

import { useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Container,
  Grid,
  Fade
} from '@mui/material';
import { motion } from 'framer-motion';
import { useTheme } from '@mui/material/styles';
import LoginIcon from '@mui/icons-material/Login';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import { useAuth } from '../auth/authContext';
import { useRouter } from 'next/navigation';
import ModelComparisonPreview from './ModelComparisonPreview';
import { useModelContext } from '../context/ModelContext';

interface HeroSectionProps {
  mode: 'light' | 'dark';
  scrollToFeatures: () => void;
}

const HeroSection: React.FC<HeroSectionProps> = ({ mode, scrollToFeatures }) => {
  const theme = useTheme();
  const { isAuthenticated, login, loading } = useAuth();
  const router = useRouter();
  // Reference to the ModelComparisonPreview component
  const modelComparisonRef = useRef<{handleCompare: () => void} | null>(null);

  // Gradient for text
  const gradientText = mode === 'dark'
    ? 'linear-gradient(90deg, #60a5fa, #a78bfa)'
    : 'linear-gradient(90deg, #3b82f6, #8b5cf6)';

  // Handle sign in or compare button click
  const handleButtonClick = async () => {
    console.log('Hero section button clicked');
    
    if (!isAuthenticated) {
      // If not authenticated, trigger login flow
      console.log('User not authenticated, triggering login');
      await login();
    } else {
      // If authenticated, handle compare action
      console.log('User authenticated, handling compare action');
      
      // Call the handleCompare method on the ModelComparisonPreview component
      if (modelComparisonRef.current && modelComparisonRef.current.handleCompare) {
        console.log('Calling handleCompare from ModelComparisonPreview');
        modelComparisonRef.current.handleCompare();
      } else {
        console.log('ModelComparisonPreview ref not available, navigating directly to compare');
        router.push('/compare');
      }
    }
  };

  return (
    <Box
      sx={{
        position: 'relative',
        minHeight: '92vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        overflow: 'hidden',
        pt: 4,
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: mode === 'dark'
            ? 'radial-gradient(circle at 30% 30%, rgba(37, 99, 235, 0.15) 0%, rgba(0, 0, 0, 0) 70%), radial-gradient(circle at 80% 80%, rgba(147, 51, 234, 0.15) 0%, rgba(0, 0, 0, 0) 70%)'
            : 'radial-gradient(circle at 30% 30%, rgba(59, 130, 246, 0.15) 0%, rgba(255, 255, 255, 0) 70%), radial-gradient(circle at 80% 80%, rgba(168, 85, 247, 0.15) 0%, rgba(255, 255, 255, 0) 70%)',
          zIndex: -1
        }
      }}
    >
      {/* Changed to full width with custom padding */}
      <Container maxWidth={false} sx={{ px: { xs: 2, sm: 3, md: 4, lg: 6 } }}>
        {/* Completely restructured to vertical layout with centered content */}
        <Box sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          width: '100%',
          maxWidth: '1000px',
          mx: 'auto',
          mb: 6
        }}>
          <Fade in={true} timeout={1000}>
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 0.2 }}
              >
                <Typography
                  variant="h2"
                  component="h1"
                  sx={{
                    fontWeight: 800,
                    mb: 2,
                    background: gradientText,
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    lineHeight: 1.2
                  }}
                >
                  Compare Leading LLMs in Real-Time
                </Typography>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 0.4 }}
              >
                <Typography
                  variant="h6"
                  sx={{
                    mb: 4,
                    fontWeight: 400,
                    maxWidth: '800px',
                    mx: 'auto',
                    color: mode === 'dark' ? 'rgba(255,255,255,0.8)' : 'text.secondary'
                  }}
                >
                  Evaluate and analyze responses from different language models side by side.
                  Get insights on performance, response time, and quality.
                </Typography>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 0.6 }}
                style={{ display: 'flex', justifyContent: 'center' }}
              >
                <Button
                  variant="contained"
                  size="large"
                  disabled={loading}
                  onClick={handleButtonClick}
                  endIcon={isAuthenticated ? <CompareArrowsIcon /> : <LoginIcon />}
                  sx={{
                    py: 1.5,
                    px: 4,
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    textTransform: 'none',
                    borderRadius: 2,
                    background: 'linear-gradient(90deg, #1976d2, #512da8)',
                    boxShadow: '0 4px 14px 0 rgba(25, 118, 210, 0.39)',
                    '&:hover': {
                      background: 'linear-gradient(90deg, #1565c0, #4527a0)',
                      boxShadow: '0 6px 20px 0 rgba(25, 118, 210, 0.5)'
                    }
                  }}
                >
                  {loading ? 'Loading...' : isAuthenticated ? 'Compare Selected Models' : 'Sign In to Compare'}
                </Button>
              </motion.div>
            </Box>
          </Fade>
        </Box>

        {/* Model comparison preview now below the text */}
        <Box sx={{ 
          width: '100%',
          maxWidth: '1800px', 
          mx: 'auto',
          mt: 2
        }}>
          <ModelComparisonPreview 
            mode={mode} 
            ref={modelComparisonRef}
          />
        </Box>
      </Container>

      {/* Scroll indicator */}
      <Box
        component={motion.div}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5, duration: 1 }}
        sx={{
          position: 'absolute',
          bottom: theme.spacing(2),
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          cursor: 'pointer'
        }}
        onClick={scrollToFeatures}
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ repeat: Infinity, duration: 2 }}
        >
          <Typography
            variant="body2"
            sx={{
              fontSize: '0.9rem',
              color: mode === 'dark' ? 'rgba(255,255,255,0.7)' : 'text.secondary'
            }}
          >
            Learn more
          </Typography>
          <Box
            sx={{
              fontSize: 20,
              mt: 1,
              textAlign: 'center',
              color: mode === 'dark' ? 'rgba(255,255,255,0.7)' : 'text.secondary'
            }}
          >
            ↓
          </Box>
        </motion.div>
      </Box>
    </Box>
  );
};

export default HeroSection;