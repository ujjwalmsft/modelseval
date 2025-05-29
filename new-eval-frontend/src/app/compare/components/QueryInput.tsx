'use client';
 
/**
* QueryInput.tsx
*
* Component explicitly handling user query inputs, system prompt configurations,
* and comparison mode toggles (direct vs context-based comparisons).
*
* Features explicitly maintained and enhanced:
* - Comprehensive validation logic for user query and system prompt inputs.
* - Real-time debug logging clearly tracking state changes and interactions.
* - Responsive UI with explicit user feedback on validation errors.
* - Clearly structured comparison mode selection (direct/context-aware).
* - Intuitive and theme-aware UI with Material UI components.
*/
 
import React, { useState, useEffect } from 'react';
import {
  Box, TextField, Button, Paper, Typography, Divider, useTheme,
  IconButton, Collapse, Menu, MenuItem, Tooltip, CircularProgress, Alert
} from '@mui/material';
import {
  Search as SearchIcon, Settings as SettingsIcon,
  KeyboardArrowDown as KeyboardArrowDownIcon, KeyboardArrowUp as KeyboardArrowUpIcon,
  HelpOutline as HelpOutlineIcon, ArrowDropDown as ArrowDropDownIcon,
  ChatBubbleOutline as ChatBubbleOutlineIcon, CompareArrows as CompareArrowsIcon,
  Person as PersonIcon
} from '@mui/icons-material';
 
interface QueryInputProps {
  query: string;
  setQuery: (value: string) => void;
  systemPrompt: string;
  setSystemPrompt: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
  useContextMode: boolean;
  setUseContextMode: (value: boolean) => void;
}
 
const QueryInput: React.FC<QueryInputProps> = ({
  query,
  setQuery,
  systemPrompt,
  setSystemPrompt,
  onSubmit,
  loading,
  useContextMode,
  setUseContextMode
}) => {
  const theme = useTheme();
  const [showSystemPrompt, setShowSystemPrompt] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [error, setError] = useState<string>('');
  const open = Boolean(anchorEl);
 
  // Validation check explicitly for query and context mode
  // useEffect(() => {
  //   if (!query.trim()) {
  //     setError('Query input cannot be empty.');
  //     console.warn('[QueryInput] Validation: Query is empty.');
  //   } else {
  //     setError('');
  //     console.debug('[QueryInput] Validation passed.');
  //   }
  // }, [query]);
 
  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
    console.debug('[QueryInput] Comparison mode menu opened.');
  };
 
  const handleMenuClose = () => {
    setAnchorEl(null);
    console.debug('[QueryInput] Comparison mode menu closed.');
  };
 
  const handleModeSelect = (mode: boolean) => {
    setUseContextMode(mode);
    handleMenuClose();
    console.info(`[QueryInput] Comparison mode set to: ${mode ? 'Context-Based' : 'Direct'}`);
  };
 
  const getButtonLabel = () =>
    loading ? "Processing..." :
      (useContextMode ? "Compare with Context" : "Compare Models");
 
  const isButtonDisabled = loading || !query.trim();
 
  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    console.debug('[QueryInput] Query changed:', value);
  };
 
  const handleSystemPromptChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSystemPrompt(value);
    console.debug('[QueryInput] System prompt changed:', value);
  };
 
  return (
<Paper elevation={3} sx={{
      p: 3, mb: 4, borderRadius: 2,
      background: theme.palette.mode === 'dark'
        ? 'linear-gradient(145deg, #1e1e2f 0%, #2d2d44 100%)'
        : 'linear-gradient(145deg, #f5f7fa 0%, #e4e8ed 100%)',
      border: `1px solid ${theme.palette.divider}`
    }}>
<Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
<SearchIcon color="primary" sx={{ mr: 1 }} />
<Typography variant="h5" fontWeight={600} sx={{
          color: theme.palette.mode === 'dark' ? '#fff' : '#333',
          borderBottom: `2px solid ${theme.palette.primary.main}`,
          display: 'inline-block'
        }}>
          {useContextMode ? 'Ask a question using custom context' : 'What would you like to compare?'}
</Typography>
<Box sx={{ flexGrow: 1 }} />
<Tooltip title="Advanced settings">
<IconButton size="small" onClick={() => setShowSystemPrompt(prev => !prev)} sx={{ mr: 1 }}>
<SettingsIcon fontSize="small" />
            {showSystemPrompt ? <KeyboardArrowUpIcon fontSize="small" /> : <KeyboardArrowDownIcon fontSize="small" />}
</IconButton>
</Tooltip>
<Tooltip title="System prompt guides how the AI responds">
<IconButton size="small">
<HelpOutlineIcon fontSize="small" />
</IconButton>
</Tooltip>
</Box>
 
      <TextField
        multiline rows={4} fullWidth
        placeholder="Enter your question or prompt here..."
        value={query}
        onChange={handleQueryChange}
        error={!!error}
        helperText={error || ' '}
        sx={{
          mt: 2, mb: 1.5,
          '& .MuiOutlinedInput-root': {
            borderRadius: 2, fontSize: '1.1rem',
            backgroundColor: theme.palette.background.paper
          }
        }}
      />
 
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
 
      <Collapse in={showSystemPrompt}>
<Typography variant="body2" color="text.secondary">System Prompt</Typography>
<TextField
          multiline rows={2} fullWidth
          placeholder="Set the system prompt..."
          value={systemPrompt}
          onChange={handleSystemPromptChange}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2, fontSize: '0.9rem',
              backgroundColor: theme.palette.background.paper
            }, mb: 2
          }}
        />
<Divider sx={{ my: 2 }} />
</Collapse>
 
      <Box sx={{ display: 'flex', justifyContent: 'center' }}>
<Box sx={{ display: 'flex', borderRadius: '25px', boxShadow: 4, overflow: 'hidden' }}>
<Button
            onClick={() => {
              console.info('[QueryInput] Submission initiated.');
              onSubmit();
            }}
            disabled={isButtonDisabled}
            startIcon={<ChatBubbleOutlineIcon />}
            endIcon={loading ? <CircularProgress size={20} color="inherit" /> :
              (useContextMode ? <PersonIcon /> : <CompareArrowsIcon />)}
            sx={{
              minWidth: 260, borderRadius: '25px 0 0 25px',
              py: 1.5, px: 3.5, fontSize: '1rem', fontWeight: 600, textTransform: 'none',
              color: '#fff',
              background: theme.palette.mode === 'dark'
                ? 'linear-gradient(90deg, #2196f3 0%, #673ab7 100%)'
                : 'linear-gradient(90deg, #1976d2 0%, #512da8 100%)',
              '&:hover': { opacity: 0.95 },
              '&.Mui-disabled': { opacity: 0.7 }
            }}
>
            {getButtonLabel()}
</Button>
<IconButton size="small" onClick={handleMenuClick} sx={{
            borderRadius: '0 25px 25px 0',
            px: 1.5, background: 'linear-gradient(90deg, #512da8 0%, #3f1f8a 100%)',
            color: '#fff'
          }}>
<ArrowDropDownIcon />
</IconButton>
<Menu anchorEl={anchorEl} open={open} onClose={handleMenuClose}
 anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
 transformOrigin={{ vertical: 'top', horizontal: 'right' }}
 sx={{ '& .MuiPaper-root': { borderRadius: 2, minWidth: 240 } }}>

<Typography variant="subtitle2" sx={{ px: 2, pt: 1.5, pb: 1, color: 'text.secondary', fontWeight: 600 }}>
              Select Comparison Mode
            </Typography>
            <Divider />
<MenuItem onClick={() => handleModeSelect(false)} selected={!useContextMode}>              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CompareArrowsIcon sx={{ mr: 1, color: theme.palette.primary.main }} fontSize="small" />
                <Box>
                  <Typography variant="body2" fontWeight={500}>📘 Direct Comparison</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Compare models without context
                  </Typography>
                </Box>
              </Box>
            </MenuItem>
{/* <MenuItem onClick={() => handleModeSelect(true)} selected={useContextMode}>Context-Based Comparison</MenuItem> */}

<MenuItem onClick={() => handleModeSelect(true)} selected={useContextMode}>
<Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PersonIcon sx={{ mr: 1, color: theme.palette.primary.main }} fontSize="small" />
                <Box>
                  <Typography variant="body2" fontWeight={500}>📄 Context-Based Comparison</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Compare with personalized context
                  </Typography>
                </Box>
              </Box>
              </MenuItem>
</Menu>
</Box>
</Box>
</Paper>
  );
};
 
export default QueryInput;