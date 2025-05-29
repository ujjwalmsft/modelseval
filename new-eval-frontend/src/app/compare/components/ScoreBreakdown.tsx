'use client';

import React, { useState } from 'react';
import { Box, Chip, Tooltip, useTheme } from '@mui/material';
import StarIcon from '@mui/icons-material/Star';
import MetricInfoCard from './MetricsInfoCard';
import { metricInfoData, MetricInfo } from './info/metricInfoData';

interface ScoreBreakdownProps {
  scores?: {
    BLEU?: number;
    ROUGE_1?: number;
    ROUGE_L?: number;
    BERTScore?: number;
    CosineSimilarity?: number;
    SemanticCosineSimilarity?: number;
    CombinedScore?: number;
    metrics?: {
      response_time?: number;
      tokens?: {
        prompt_tokens?: number;
        completion_tokens?: number;
        total_tokens?: number;
      };
      tokens_per_second?: number;
    };
  };
}

const ScoreBreakdown: React.FC<ScoreBreakdownProps> = ({ scores = {} }) => {
  const theme = useTheme();
  const [infoOpen, setInfoOpen] = useState(false);
  const [selectedMetric, setSelectedMetric] = useState<MetricInfo | null>(null);

  const cosineSim = scores.SemanticCosineSimilarity ?? scores.CosineSimilarity;
  const perf = scores.metrics || {};

  // First row: BLEU, ROUGE-1, ROUGE-L, Tokens/sec
  const firstRow = [
    { label: 'BLEU', value: scores.BLEU },
    { label: 'ROUGE-1', value: scores.ROUGE_1 },
    { label: 'ROUGE-L', value: scores.ROUGE_L },
    { label: 'Tokens/sec', value: perf.tokens_per_second },
  ];

  // Second row: Semantic Cosine Similarity, Combined Score
  const secondRow = [
    { label: 'Cosine Similarity', value: cosineSim },
    { label: 'Combined', value: scores.CombinedScore, highlight: true },
  ];

  const handleChipClick = (label: string) => {
    const info = metricInfoData[label];
    if (info) {
      setSelectedMetric(info);
      setInfoOpen(true);
    }
  };

  return (
    <Box sx={{ pt: 2.5, px: 3, mt: 2, display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
      {/* First row */}
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: 3,
          width: '100%',
          mb: 2,
        }}
      >
        {firstRow.map(
          ({ label, value }) =>
            value !== undefined &&
            !isNaN(value) && (
              <Tooltip title={`${label} Score`} arrow placement="top" key={label}>
                <Chip
                  label={`${label}: ${value.toFixed(3)}`}
                  size="medium"
                  onClick={() => handleChipClick(label)}
                  sx={{
                    fontSize: '1.15rem',
                    fontWeight: 600,
                    backgroundColor:
                      theme.palette.mode === 'dark'
                        ? 'rgba(255,255,255,0.10)'
                        : 'rgba(0,0,0,0.08)',
                    color: theme.palette.text.primary,
                    px: 3,
                    py: 2,
                    minWidth: 180,
                    maxWidth: 260,
                    cursor: 'pointer',
                  }}
                />
              </Tooltip>
            )
        )}
      </Box>
      {/* Second row: Semantic Cosine Similarity and Combined Score */}
      <Box
        sx={{
          display: 'flex',
          pt: 3,
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: 3,
          width: '100%',
          mb: 1,
        }}
      >
        {secondRow.map(({ label, value, highlight }) =>
          value !== undefined && !isNaN(value) ? (
            <Tooltip
              title={
                label === 'Semantic Cosine Similarity'
                  ? 'Semantic Cosine Similarity Score'
                  : `${label} Score`
              }
              arrow
              placement="top"
              key={label}
            >
              <Chip
                icon={highlight ? <StarIcon /> : undefined}
                label={
                  highlight
                    ? `Combined: ${value.toFixed(3)}`
                    : `${label}: ${value.toFixed(3)}`
                }
                size={highlight ? 'large' : 'medium'}
                onClick={() => handleChipClick(label)}
                sx={{
                  fontSize: highlight ? '1.35rem' : '1.15rem',
                  fontWeight: highlight ? 700 : 600,
                  backgroundColor: highlight
                    ? theme.palette.primary.main
                    : theme.palette.mode === 'dark'
                    ? 'rgba(255,255,255,0.10)'
                    : 'rgba(0,0,0,0.08)',
                  color: highlight
                    ? theme.palette.primary.contrastText
                    : theme.palette.text.primary,
                  px: highlight ? 4 : 3,
                  py: highlight ? 2.5 : 2,
                  minWidth: highlight ? 240 : 220,
                  maxWidth: highlight ? 340 : 320,
                  boxShadow: highlight ? theme.shadows[2] : undefined,
                  whiteSpace: 'normal',
                  textAlign: 'center',
                  cursor: 'pointer',
                }}
              />
            </Tooltip>
          ) : null
        )}
      </Box>
      {/* Metric Info Card Modal */}
      {selectedMetric && (
        <MetricInfoCard
          open={infoOpen}
          onClose={() => setInfoOpen(false)}
          metric={selectedMetric}
        />
      )}
    </Box>
  );
};

export default ScoreBreakdown;