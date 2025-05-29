'use client';

import React from 'react';
import { Box, Typography, Chip, Tooltip, useTheme } from '@mui/material';

interface JudgeScores {
  personalization?: number;
  relevance?: number;
  fluency?: number;
  coherence?: number;
  creativity?: number;
  reasons?: {
    personalization?: string;
    relevance?: string;
    fluency?: string;
    coherence?: string;
    creativity?: string;
  };
}

interface JudgeSummaryProps {
  scores?: JudgeScores;
}

const scoreLabels = [
  { key: 'personalization', label: 'Personalization' },
  { key: 'relevance', label: 'Relevance' },
  { key: 'fluency', label: 'Fluency' },
  { key: 'coherence', label: 'Coherence' },
  { key: 'creativity', label: 'Creativity' },
];

// Definitions for each metric
const judgeMetricDefinitions: Record<string, string> = {
  personalization:
    'Personalization measures how well the response is tailored to the user’s context, preferences, or prior information.',
  relevance:
    'Relevance assesses how well the response addresses the prompt or question, staying on topic and providing useful information.',
  fluency:
    'Fluency evaluates the grammatical correctness, readability, and natural flow of the response.',
  coherence:
    'Coherence checks if the response is logically consistent and well-structured, with ideas that connect smoothly.',
  creativity:
    'Creativity measures the originality and inventiveness of the response, including novel ideas or engaging phrasing.',
};

const JudgeSummary: React.FC<JudgeSummaryProps> = ({ scores = {} }) => {
  const theme = useTheme();

  if (!scores) return null;

  return (
    <Box
      sx={{
        pt: 2.5,
        mt: 1.5,
        display: 'flex',
        flexDirection: 'row',
        gap: 3,
        justifyContent: 'center',
        flexWrap: 'wrap',
      }}
    >
      {scoreLabels.map(({ key, label }) => {
        const value = (scores as any)[key];
        const reason = scores.reasons?.[key as keyof typeof scores.reasons];
        if (value === undefined || isNaN(value)) return null;
        return (
          <Box
            key={key}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              minWidth: 220,
              maxWidth: 340,
              flex: 1,
              mx: 1,
            }}
          >
            <Tooltip
  title={
    <Typography sx={{ fontSize: '1.15rem', fontWeight: 500, px: 1 }}>
      {judgeMetricDefinitions[key] || 'No definition available.'}
    </Typography>
  }
  arrow
  placement="top"
  componentsProps={{
    tooltip: {
      sx: {
        bgcolor: theme.palette.background.paper,
        color: theme.palette.text.primary,
        boxShadow: 3,
        p: 2,
        maxWidth: 340,
        borderRadius: 2,
      },
    },
    arrow: {
      sx: {
        color: theme.palette.background.paper,
      },
    },
  }}
>
  <Chip
    label={`${label}: ${value}/10`}
    size="medium"
    sx={{
      fontSize: '1.15rem',
      fontWeight: 600,
      backgroundColor:
        theme.palette.mode === 'dark'
          ? 'rgba(255,255,255,0.08)'
          : 'rgba(0,0,0,0.08)',
      color: theme.palette.text.primary,
      px: 2,
      py: 1,
      mb: 2,
      cursor: 'help',
    }}
  />
</Tooltip>
            {reason && (
              <Typography
                variant="body1"
                color="text.secondary"
                sx={{
                  textAlign: 'center',
                  fontSize: '1.15rem',
                  fontWeight: 500,
                  width: '100%',
                  minHeight: 48,
                }}
              >
                {reason}
              </Typography>
            )}
          </Box>
        );
      })}
    </Box>
  );
};

export default JudgeSummary;