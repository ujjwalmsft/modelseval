'use client';

import React from 'react';
import { 
  Box, 
  ToggleButtonGroup, 
  ToggleButton, 
  Typography, 
  Paper, 
  useTheme,
  Divider,
  Tooltip
} from '@mui/material';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import PersonIcon from '@mui/icons-material/Person';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';

interface ComparisonModeSelectorProps {
  useContextMode: boolean;
  setUseContextMode: (value: boolean) => void;
}

const ComparisonModeSelector: React.FC<ComparisonModeSelectorProps> = ({
  useContextMode,
  setUseContextMode
}) => {
  const theme = useTheme();
  
  const handleModeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newMode: boolean | null
  ) => {
    // Don't allow deselecting both options
    if (newMode !== null) {
      setUseContextMode(newMode);
    }
  };
  
  return (
    <Paper
      elevation={1}
      sx={{
        p: 3,
        mb: 4,
        borderRadius: 2,
        background: theme.palette.mode === 'dark'
          ? 'rgba(255,255,255,0.02)'
          : 'rgba(0,0,0,0.02)',
        border: `1px solid ${theme.palette.divider}`
      }}
    >
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CompareArrowsIcon color="primary" />
          <Typography variant="h6" fontWeight={600}>
            Comparison Mode
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <InfoOutlinedIcon fontSize="small" color="action" />
          <Typography variant="body2" color="text.secondary">
            Choose how models should process your query
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ mb: 2 }} />

      <ToggleButtonGroup
        value={useContextMode}
        exclusive
        onChange={handleModeChange}
        aria-label="comparison mode"
        fullWidth
        sx={{
          '& .MuiToggleButtonGroup-grouped': {
            border: `1px solid ${theme.palette.divider} !important`,
            '&.Mui-selected': {
              backgroundColor: theme.palette.primary.main + '20', // Transparent version of primary color
              color: theme.palette.primary.main
            }
          }
        }}
      >
        <ToggleButton 
          value={false} 
          aria-label="direct comparison"
          sx={{ 
            py: 1.5, 
            borderTopLeftRadius: '8px !important', 
            borderBottomLeftRadius: '8px !important' 
          }}
        >
          <Tooltip title="Models respond directly to your query without additional context">
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
              <CompareArrowsIcon />
              <Typography variant="body2" fontWeight={500}>
                Direct Comparison
              </Typography>
            </Box>
          </Tooltip>
        </ToggleButton>
        
        <ToggleButton 
          value={true} 
          aria-label="context-aware comparison"
          sx={{ 
            py: 1.5, 
            borderTopRightRadius: '8px !important', 
            borderBottomRightRadius: '8px !important' 
          }}
        >
          <Tooltip title="Models take into account context information you provide">
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
              <PersonIcon />
              <Typography variant="body2" fontWeight={500}>
                Context-Aware
              </Typography>
            </Box>
          </Tooltip>
        </ToggleButton>
      </ToggleButtonGroup>
      
      <Typography 
        variant="body2" 
        color="text.secondary"
        sx={{ mt: 2, fontStyle: 'italic' }}
      >
        {useContextMode 
          ? "Provides context information with your query to test model personalization" 
          : "Compare responses to your query without additional context information"}
      </Typography>
    </Paper>
  );
};

export default ComparisonModeSelector;