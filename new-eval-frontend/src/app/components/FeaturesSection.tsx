/**
 * Features showcase component with auto-rotating highlights.
 * 
 * Presents key product benefits using an animated card grid layout.
 * Implements automatic rotation between features with a 5-second interval.
 * Features responsive grid layout with optimized spacing and alignment.
 * Uses gradient text headers for visual emphasis and brand consistency.
 * Provides interactive feature selection through card click events.
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Container,
  Grid,
  useTheme
} from '@mui/material';
import { featureData } from '../content/featureData';
import FeatureCard from './FeatureCard';

interface FeaturesSectionProps {
  mode: 'light' | 'dark';
  featuresSectionRef: React.RefObject<HTMLDivElement>;
}

const FeaturesSection: React.FC<FeaturesSectionProps> = ({ mode, featuresSectionRef }) => {
  const theme = useTheme();
  const [visibleSection, setVisibleSection] = useState(0);
  
  // Gradient for text
  const gradientText = mode === 'dark'
    ? 'linear-gradient(90deg, #60a5fa, #a78bfa)'
    : 'linear-gradient(90deg, #3b82f6, #8b5cf6)';
  
  // Auto-scroll through features section
  useEffect(() => {
    const interval = setInterval(() => {
      setVisibleSection(prev => (prev + 1) % featureData.length);
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <Box
      ref={featuresSectionRef}
      sx={{ py: 10, bgcolor: mode === 'dark' ? 'rgba(10,10,14,0.8)' : 'rgba(248,250,252,0.8)' }}
    >
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <Typography
            variant="h3"
            gutterBottom
            sx={{
              fontWeight: 700,
              background: gradientText,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            Why Compare Language Models?
          </Typography>
          <Typography
            variant="h6"
            sx={{
              maxWidth: 700,
              mx: 'auto',
              color: mode === 'dark' ? 'rgba(255,255,255,0.8)' : 'text.secondary'
            }}
          >
            Make informed decisions about which AI models best suit your specific use cases
          </Typography>
        </Box>

        <Grid 
          container 
          spacing={6} 
          sx={{ 
            justifyContent: 'center',
            maxWidth: 1200,
            mx: 'auto'  
          }}
        >
          {featureData.map((feature, index) => (
            <Grid 
              item={true}
              xs={12} 
              md={6} 
              key={index} 
              sx={{ 
                display: 'flex',
                justifyContent: 'center',
                padding: 0 // Match your original styling
              }}
            >
              {/* This Box wrapper with fixed dimensions is crucial */}
              <Box sx={{ 
                height: 320, 
                width: '100%',
                maxWidth: 500
              }}>
                <FeatureCard
                  icon={feature.icon}
                  title={feature.title}
                  description={feature.description}
                  index={index}
                  isActive={visibleSection === index}
                  onClick={() => setVisibleSection(index)}
                  mode={mode}
                />
              </Box>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
};

export default FeaturesSection;