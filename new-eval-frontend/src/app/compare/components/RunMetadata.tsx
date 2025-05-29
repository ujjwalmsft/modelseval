import React from 'react';
import { Box, Chip, Tooltip, useTheme } from '@mui/material';

interface RunMetadataProps {
  responseTime?: number;
  promptTokens?: number;
  completionTokens?: number;
  totalTokens?: number;
  timestamp?: string;
}

const RunMetadata: React.FC<RunMetadataProps> = ({
  responseTime,
  promptTokens,
  completionTokens,
  totalTokens,
  timestamp,
}) => {
  const theme = useTheme();

  const renderChip = (label: string, value?: string | number) => {
    if (value === undefined || value === null) return null;
    return (
      <Tooltip title={label} key={label}>
        <Chip
          label={`${label}: ${value}`}
          size="medium"
          sx={{
            fontSize: '1rem',
            fontWeight: 400,
            px: 2.5,
            py: 1.5,
            minWidth: 120,
            backgroundColor: theme.palette.mode === 'dark'
              ? 'rgba(255,255,255,0.10)'
              : 'rgba(0,0,0,0.08)',
            color: theme.palette.text.primary,
            mb: 1,
          }}
        />
      </Tooltip>
    );
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 2,
        width: '100%',
        flexWrap: 'wrap',
      }}
    >
      {renderChip('Latency', responseTime ? `${responseTime.toFixed(2)}s` : undefined)}
      {renderChip('Prompt Tokens', promptTokens)}
      {renderChip('Completion Tokens', completionTokens)}
      {renderChip('Total Tokens', totalTokens)}
    </Box>
  );
};

export default RunMetadata;