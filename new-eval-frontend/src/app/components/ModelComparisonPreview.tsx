/**
 * Animated preview component showcasing model comparison interface.
 * 
 * Presents a visually appealing mock-up of the comparison feature with sample models.
 * Uses Framer Motion for staggered entrance animations and 3D perspective effects.
 * Implements theme-aware styling with custom gradients and backdrop filters.
 * Features decorative elements with floating gradient orbs for visual interest.
 * Displays model response times with consistent color-coding for each provider.
 */

'use client';

import React, { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import { Box, Paper, Typography, Chip, Fade, Checkbox, useTheme, Grid, Snackbar, Alert } from '@mui/material';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useModelContext } from '../context/ModelContext';

interface ModelComparisonPreviewProps {
  mode: 'light' | 'dark';
}

// Define the ref interface to expose the handleCompare method
export interface ModelComparisonPreviewRef {
  handleCompare: () => void;
}

// Extended model data to include new models and disabled flag
const allModels = [
  // First card models
  {
    name: 'GPT-4',
    color: '#10a37f',
    responseTime: '0.9s',
    disabled: false
  },
  {
    name: 'Claude 3',
    color: '#7963d2',
    responseTime: '0.7s',
    disabled: true,  // Mark as disabled
    comingSoon: true // Add a comingSoon flag
  },
  {
    name: 'Gemini Pro',
    color: '#4285f4',
    responseTime: '0.8s',
    disabled: true,  // Mark as disabled
    comingSoon: true // Add a comingSoon flag
  },
  {
    name: 'O1-mini',
    color: '#9c55f5',
    responseTime: '0.5s',
    disabled: false
  },
  // Second card models
  {
    name: 'DeepSeek-R1',
    color: '#ff6b6b',
    responseTime: '0.6s',
    disabled: false
  },
  {
    name: 'Phi-4',
    color: '#00abcc',
    responseTime: '0.7s',
    disabled: false
  },
  {
    name: 'Llama 3',
    color: '#ff9e43',
    responseTime: '0.8s',
    disabled: false
  },
  {
    name: 'GPT-4.1-nano',
    color: '#0ea47f',
    responseTime: '0.4s',
    disabled: false
  }
];

// Split the models between the two cards
const firstCardModels = allModels.slice(0, 4);
const secondCardModels = allModels.slice(4);

const ModelComparisonPreview = forwardRef<ModelComparisonPreviewRef, ModelComparisonPreviewProps>(({ mode }, ref) => {
  const theme = useTheme();
  const router = useRouter();
  const { setSelectedModelIds } = useModelContext();
  
  // Initialize state with no models selected
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  
  // Add state for toast
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  // Calculate if we have exactly 4 models selected
  const hasExactlyFourModels = selectedModels.length === 4;

  // Handle model selection
  const handleModelSelect = (modelName: string) => {
    console.log(`ModelComparisonPreview - Model clicked: ${modelName}`);
    
    // Check if model is disabled
    const modelInfo = allModels.find(model => model.name === modelName);
    if (modelInfo?.disabled) {
      // Show toast for disabled model
      setToastMessage(`${modelName} coming soon!`);
      setToastOpen(true);
      return;
    }
    
    setSelectedModels(prev => {
      if (prev.includes(modelName)) {
        // Remove the model if already selected
        const newSelection = prev.filter(name => name !== modelName);
        console.log(`ModelComparisonPreview - Removed model, new selection:`, newSelection);
        return newSelection;
      } else {
        // Add the model if we have less than 4 selected
        if (prev.length < 4) {
          const newSelection = [...prev, modelName];
          console.log(`ModelComparisonPreview - Added model, new selection:`, newSelection);
          return newSelection;
        }
        // Otherwise don't change selection
        console.log(`ModelComparisonPreview - Already have 4 models, not adding more`);
        return prev;
      }
    });
  };

  // Log selected models for debugging
  useEffect(() => {
    console.log('ModelComparisonPreview - Currently selected models:', selectedModels);
  }, [selectedModels]);
  
  // Handle compare button click
  const handleCompare = () => {
    console.log('*** CLICK HANDLER TRIGGERED ***');
    
    if (hasExactlyFourModels) {
      try {
        // Map model names to their IDs
        const modelNameToId: Record<string, string> = {
          'GPT-4': 'gpt4',
          'Claude 3': 'claude3',
          'Gemini Pro': 'gemini',
          'O1-mini': 'o1mini',
          'DeepSeek-R1': 'deepseek',
          'Phi-4': 'phi4',
          'Llama 3': 'llama',
          'GPT-4.1-nano': 'gpt4nano'
        };
        
        // Map model names to their IDs
        const modelIds = selectedModels.map(name => {
          const id = modelNameToId[name];
          if (!id) {
            console.error(`No ID mapping found for model: ${name}`);
            return name.toLowerCase().replace(' ', '');
          }
          return id;
        });
        
        // FIRST: Update the context with selected models
        console.log('ModelComparisonPreview - Setting context model IDs:', modelIds);
        setSelectedModelIds(modelIds);
        
        // SECOND: Also store in localStorage as backup
        try {
          localStorage.setItem('selectedModelIds', JSON.stringify(modelIds));
          console.log('ModelComparisonPreview - Saved to localStorage:', modelIds);
        } catch (storageError) {
          console.warn('Error saving to localStorage:', storageError);
        }
        
        // THIRD: Navigate using standard Next.js router
        console.log('ModelComparisonPreview - Navigating to /compare');
        router.push('/compare');
      } catch (error) {
        console.error('Error in handleCompare:', error);
        router.push('/compare');
      }
    } else {
      console.log('ModelComparisonPreview - Must select exactly 4 models');
      alert('Please select exactly 4 models to compare');
    }
  };

  // Expose the handleCompare method to parent components through ref
  useImperativeHandle(ref, () => ({
    handleCompare
  }));

  // Gradient scheme based on theme mode
  const gradient = mode === 'dark'
    ? 'linear-gradient(135deg, rgba(13,17,23,0.9) 0%, rgba(20,29,47,0.9) 100%)'
    : 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,242,245,0.9) 100%)';

  const renderModelCard = (models: typeof firstCardModels, title: string) => (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.7, delay: 0.8 }}
      style={{ width: '100%' }}
    >
      <Paper
        elevation={8}
        sx={{
          p: { xs: 2, sm: 3, md: 3 }, // Slightly reduced padding
          borderRadius: 4,
          background: gradient,
          backdropFilter: 'blur(20px)',
          border: '1px solid',
          borderColor: mode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
          transform: 'perspective(1500px) rotateY(-5deg)',
          transformStyle: 'preserve-3d',
          overflow: 'hidden',
          width: '100%',
          height: '100%',
          maxWidth: '700px', // Added max width constraint
          mx: 'auto', // Center the card
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          mb: 2,
          width: '100%', // Ensure title container takes full width
        }}>
          <Typography variant="h6" fontWeight={600} sx={{ flexGrow: 1 }}>{title}</Typography>
          <Box sx={{ display: 'flex', gap: 1, flexShrink: 0 }}>
            {[1, 2, 3].map(i => (
              <Box key={i} sx={{ width: 10, height: 10, borderRadius: '50%', background: i === 1 ? '#f87171' : i === 2 ? '#fbbf24' : '#34d399' }} />
            ))}
          </Box>
        </Box>

        <Typography variant="subtitle2" sx={{ mb: 1, opacity: 0.8, textAlign: 'center' }}>
          {hasExactlyFourModels 
            ? "Ready to compare 4 selected models" 
            : `Select 4 models to compare (${selectedModels.length}/4)`
          }
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 3 }}>
          {models.map((model, idx) => (
            <motion.div
              key={model.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 1 + (idx * 0.2) }}
            >
              <Paper
                sx={{
                  p: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  borderLeft: `4px solid ${selectedModels.includes(model.name) ? model.color : 'transparent'}`,
                  background: mode === 'dark' 
                    ? selectedModels.includes(model.name) ? 'rgba(40,55,71,0.7)' : 'rgba(30,41,59,0.5)'
                    : selectedModels.includes(model.name) ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.8)',
                  transition: 'all 0.2s ease',
                  cursor: model.disabled ? 'not-allowed' : 'pointer',
                  opacity: model.disabled ? 0.6 : 1,
                  '&:hover': {
                    boxShadow: model.disabled ? 0 : 3,
                    transform: model.disabled ? 'none' : 'translateY(-2px)'
                  },
                  position: 'relative'
                }}
                onClick={() => handleModelSelect(model.name)}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <Checkbox
                    checked={selectedModels.includes(model.name)}
                    size="small"
                    sx={{
                      color: model.color,
                      padding: 0,
                      '&.Mui-checked': { color: model.color },
                      opacity: model.disabled ? 0.5 : 1,
                      pointerEvents: model.disabled ? 'none' : 'auto'
                    }}
                    onClick={(e) => {
                      if (!model.disabled) {
                        e.stopPropagation();
                      }
                    }}
                    onChange={() => {
                      if (!model.disabled) {
                        handleModelSelect(model.name);
                      }
                    }}
                    disabled={model.disabled}
                  />
                  <Box
                    sx={{
                      width: 24,
                      height: 24,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: `${model.color}22`,
                      color: model.color
                    }}
                  >
                    {model.name.charAt(0)}
                  </Box>
                  <Typography variant="body2" fontWeight={500}>
                    {model.name}
                  </Typography>
                  
                  {/* Add Coming Soon chip for disabled models */}
                  {model.comingSoon && (
                    <Chip 
                      label="Coming Soon" 
                      size="small" 
                      color="secondary"
                      sx={{ 
                        ml: 1, 
                        height: 20, 
                        fontSize: '0.65rem',
                        fontWeight: 'bold'
                      }}
                    />
                  )}
                </Box>
                <Chip
                  label={model.responseTime}
                  size="small"
                  sx={{
                    fontWeight: 500,
                    background: `${model.color}22`,
                    borderColor: `${model.color}44`,
                    fontSize: '0.7rem',
                    opacity: model.disabled ? 0.7 : 1
                  }}
                />
              </Paper>
            </motion.div>
          ))}
        </Box>
      </Paper>
    </motion.div>
  );

  return (
    <Fade in={true} timeout={1500}>
      <Box sx={{ 
        width: '100%', 
        overflow: 'visible', 
        mx: 'auto',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <Grid 
          container 
          spacing={{ xs: 3, md: 4 }} // Reduced spacing to keep cards closer horizontally
          sx={{ 
            justifyContent: 'center',
            maxWidth: '2000px',
            mx: 'auto',
            px: { xs: 2, sm: 3, md: 4 }
          }}
        >
          {/* First Card */}
          <Grid item xs={12} md={6} sx={{ 
            maxWidth: { xs: '100%', sm: '700px', md: '700px' }, // Reduced from 850px
            minWidth: { md: '500px' } // Reduced from 850px to avoid forcing them to be too wide
          }}>
            <Box sx={{
              position: 'relative',
              height: '100%',
              width: '100%'
            }}>
              {renderModelCard(firstCardModels, " Models")} {/* Shorter title */}
              {/* Floating decorative elements */}
              <Box sx={{
                position: 'absolute',
                top: -30,
                right: -40,
                width: 100,
                height: 100,
                borderRadius: '50%',
                background: theme.palette.primary.main,
                opacity: 0.1,
                filter: 'blur(40px)'
              }} />
              <Box sx={{
                position: 'absolute',
                bottom: 0,
                left: -60,
                width: 150,
                height: 150,
                borderRadius: '50%',
                background: theme.palette.secondary.main,
                opacity: 0.1,
                filter: 'blur(60px)'
              }} />
            </Box>
          </Grid>
  
          {/* Second Card */}
          <Grid item xs={12} md={6} sx={{ 
            maxWidth: { xs: '100%', sm: '700px', md: '700px' }, // Reduced from 850px
            minWidth: { md: '500px' } // Reduced from 850px to avoid forcing them to be too wide
          }}>
            <Box sx={{
              position: 'relative',
              height: '100%',
              width: '100%'
            }}>
              {renderModelCard(secondCardModels, " Models")} {/* Shorter title */}
              {/* Floating decorative elements */}
              <Box sx={{
                position: 'absolute',
                top: -30,
                right: -40,
                width: 100,
                height: 100,
                borderRadius: '50%',
                background: theme.palette.secondary.main,
                opacity: 0.1,
                filter: 'blur(40px)'
              }} />
              <Box sx={{
                position: 'absolute',
                bottom: 0,
                left: -60,
                width: 150,
                height: 150,
                borderRadius: '50%',
                background: theme.palette.primary.main,
                opacity: 0.1,
                filter: 'blur(60px)'
              }} />
            </Box>
          </Grid>
        </Grid>
        
        {/* Toast notification */}
        <Snackbar
          open={toastOpen}
          autoHideDuration={3000}
          onClose={() => setToastOpen(false)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            onClose={() => setToastOpen(false)} 
            severity="info" 
            variant="filled"
            sx={{ width: '100%' }}
          >
            {toastMessage}
          </Alert>
        </Snackbar>
      </Box>
    </Fade>
  );
});

ModelComparisonPreview.displayName = 'ModelComparisonPreview';

export default ModelComparisonPreview;