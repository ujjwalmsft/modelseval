/**
 * Interactive feature card component with animated transitions.
 * 
 * Displays a feature with icon, title, and description in an elevated card layout.
 * Implements smooth animations using Material UI's Grow component for entrance effects.
 * Provides interactive states with hover and active visual feedback.
 * Features theme-aware styling with proper light/dark mode adaptations.
 * Uses elevation and scaling transforms to create depth hierarchy in the interface.
 */

'use client';

import {
  Box,
  Typography,
  Card,
  CardContent,
  useTheme
} from '@mui/material';
import { Grow } from '@mui/material';
import { ReactNode } from 'react';

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  index: number;
  isActive: boolean;
  onClick: () => void;
  mode: 'light' | 'dark';
}

const FeatureCard: React.FC<FeatureCardProps> = ({ 
  icon, 
  title, 
  description, 
  index, 
  isActive, 
  onClick,
  mode
}) => {
  const theme = useTheme();

  return (
    <Box sx={{ 
      height: 320, 
      width: '100%', 
    }}>
      <Grow in={true} timeout={(index + 1) * 500}>
        <Card
          sx={{
            height: '100%',
            width: '100%', 
            display: 'flex',
            flexDirection: 'column',
            borderRadius: 4,
            transition: 'all 0.3s ease',
            border: '1px solid',
            borderColor: theme.palette.divider,
            opacity: isActive ? 1 : 0.7,
            transform: isActive ? 'scale(1.03)' : 'scale(1)',
            boxShadow: isActive ?
              (mode === 'dark' ? '0 8px 32px rgba(0,0,0,0.5)' : '0 8px 32px rgba(0,0,0,0.1)') :
              'none',
            '&:hover': {
              borderColor: theme.palette.primary.main,
              transform: 'translateY(-5px)',
              boxShadow: mode === 'dark' ? '0 12px 40px rgba(0,0,0,0.6)' : '0 12px 40px rgba(0,0,0,0.15)'
            }
          }}
          onClick={onClick}
        >
          <CardContent 
            sx={{ 
              p: 4, 
              display: 'flex', 
              flexDirection: 'column', 
              height: '100%',
              justifyContent: 'space-between'
            }}
          >
            <Box>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: isActive ?
                    (mode === 'dark' ? 'rgba(37, 99, 235, 0.2)' : 'rgba(59, 130, 246, 0.1)') :
                    (mode === 'dark' ? 'rgba(30, 41, 59, 0.5)' : 'rgba(241, 245, 249, 0.8)'),
                  color: theme.palette.primary.main,
                  mb: 2,
                  transition: 'all 0.3s ease'
                }}
              >
                {icon}
              </Box>
              <Typography variant="h5" component="h3" fontWeight={600} gutterBottom>
                {title}
              </Typography>
            </Box>
            
            <Typography
              variant="body1"
              sx={{
                color: mode === 'dark' ? 'rgba(255,255,255,0.8)' : 'text.secondary'
              }}
            >
              {description}
            </Typography>
          </CardContent>
        </Card>
      </Grow>
    </Box>
  );
};

export default FeatureCard;