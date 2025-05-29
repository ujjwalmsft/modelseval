'use client';

import React from 'react';
import { Box, Typography, Chip, Tooltip, useTheme } from '@mui/material';

/**
* EvaluationMetrics.tsx
*
* Displays quantitative evaluation metrics received from the Evaluator agent (via polling).
* Metrics displayed include BLEU, ROUGE-1, ROUGE-L, BERTScore, and Cosine Similarity.
*
* Features:
* - Robust data handling and detailed debug logging.
* - Intuitive visual representation with tooltips for clarity.
*/

interface EvaluationMetricsProps {
  metrics?: {
    BLEU?: number;
    ROUGE_1?: number;
    ROUGE_L?: number;
    BERTScore?: number;
    CosineSimilarity?: number;
  };
}

const EvaluationMetrics: React.FC<EvaluationMetricsProps> = ({ metrics }) => {
  const theme = useTheme();

  const renderMetric = (label: string, value?: number) => {
    if (value === undefined || isNaN(value)) {
      return null;
    }
    return (
      <Tooltip title={`${label} Score`} arrow placement="top" key={label}>
        <Chip
          label={`${label}: ${value.toFixed(2)}`}
          size="small"
          sx={{
            fontSize: '0.75rem',
            fontWeight: 500,
            backgroundColor:
              theme.palette.mode === 'dark'
                ? 'rgba(255,255,255,0.05)'
                : 'rgba(0,0,0,0.05)',
            color: theme.palette.text.primary,
          }}
        />
      </Tooltip>
    );
  };

  if (!metrics) {
    return null;
  }

  return (
    <Box sx={{ mt: 1.5, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
      <Typography variant="subtitle2">Quantitative Evaluation</Typography>
      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        {renderMetric('BLEU', metrics.BLEU)}
        {renderMetric('ROUGE-1', metrics.ROUGE_1)}
        {renderMetric('ROUGE-L', metrics.ROUGE_L)}
        {renderMetric('BERTScore', metrics.BERTScore)}
        {renderMetric('Cosine Similarity', metrics.CosineSimilarity)}
      </Box>
    </Box>
  );
};

export default EvaluationMetrics;