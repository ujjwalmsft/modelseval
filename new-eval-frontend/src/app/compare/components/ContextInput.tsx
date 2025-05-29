'use client';
 
/**
* ContextInput.tsx
*
* Allows users to provide additional contextual information explicitly.
* This context is crucial when the system is running in context-aware mode.
*
* Features:
* - Explicit validation to ensure context is provided in context-aware scenarios.
* - User-friendly error feedback clearly displayed when validation fails.
* - Comprehensive debug logging for state changes and validation events.
* - Responsive and theme-aware design using Material UI.
*/
 
import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, useTheme, Divider, TextField, Alert } from '@mui/material';
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
 
interface ContextInputProps {
  context: string;
  setContext: (value: string) => void;
  useContextMode?: boolean;  // Added explicitly for validation
}
 
const ContextInput: React.FC<ContextInputProps> = ({ context, setContext, useContextMode = false }) => {
  const theme = useTheme();
  const [error, setError] = useState<string>('');
 
  // Explicitly validate context when useContextMode changes or context updates
  useEffect(() => {
    if (useContextMode && !context.trim()) {
      const errorMsg = 'Context is required when context-aware mode is enabled.';
      setError(errorMsg);
      console.warn('[ContextInput] Validation error:', errorMsg);
    } else {
      setError('');
      console.debug('[ContextInput] Context validation passed.');
    }
  }, [context, useContextMode]);
 
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    console.debug('[ContextInput] Context changed:', newValue);
    setContext(newValue);
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
<DescriptionOutlinedIcon color="primary" />
<Typography variant="h6" fontWeight={600}>
            Context {useContextMode ? '(Required)' : '(Optional)'}
</Typography>
</Box>
<Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
<InfoOutlinedIcon fontSize="small" color="action" />
<Typography variant="body2" color="text.secondary">
            Provide custom user info like preferences, health, or background
</Typography>
</Box>
</Box>
 
      <Divider sx={{ mb: 2 }} />
 
      <TextField
        multiline
        rows={4}
        fullWidth
        placeholder="e.g., Mr. X is 65 years old, enjoys museums, avoids seafood, has arthritis..."
        value={context}
        onChange={handleChange}
        error={!!error}
        helperText={error || ' '}
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: 2,
            backgroundColor: theme.palette.background.paper,
          }
        }}
      />
 
      {error && (
<Alert severity="error" sx={{ mt: 2 }}>
          {error}
</Alert>
      )}
</Paper>
  );
};
 
export default ContextInput;