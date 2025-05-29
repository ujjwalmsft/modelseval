'use client';

import React, { useState, useEffect } from 'react';
import { Tabs, Tab, Box, Typography } from '@mui/material';
import JudgeSummary from './JudgeSummary';
import ScoreBreakdown from './ScoreBreakdown';

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

interface EvaluationScores {
  BLEU?: number;
  ROUGE_1?: number;
  ROUGE_L?: number;
  BERTScore?: number;
  CosineSimilarity?: number;
}

interface ModelResponseTabsProps {
  response?: string;
  judgeScores?: JudgeScores;
  evaluationScores?: EvaluationScores;
  loading?: boolean;
  agentResultsAvailable?: boolean;
}

const ModelResponseTabs: React.FC<ModelResponseTabsProps> = ({
  response,
  judgeScores,
  evaluationScores,
  loading = false,
  agentResultsAvailable = false,
}) => {
  const [tab, setTab] = useState(0);

  // Only show tabs that are available
  const tabs = [
    { label: 'Response', show: true },
    { label: 'Judge', show: agentResultsAvailable },
    { label: 'Evaluation', show: agentResultsAvailable },
  ].filter(t => t.show);

  // Reset to Response tab if agent results become unavailable
  useEffect(() => {
    if (!agentResultsAvailable && tab > 0) setTab(0);
  }, [agentResultsAvailable, tab]);

  return (
    <Box>
      <Tabs
        value={tab}
        onChange={(_, v) => setTab(v)}
        variant="fullWidth"
        sx={{ minHeight: 36, mb: 1 }}
      >
        {tabs.map((t, i) => (
          <Tab key={t.label} label={t.label} sx={{ minHeight: 36, fontWeight: 500 }} />
        ))}
      </Tabs>
      <Box sx={{ minHeight: 80 }}>
        {tabs[tab].label === 'Response' && (
          loading ? (
            <Typography
  variant="body2"
  sx={{
    fontSize: '1.25rem', // or '1.3rem', adjust as needed
    lineHeight: 1.7,
    color: theme => theme.palette.text.secondary,
    textAlign: 'left',
    wordBreak: 'break-word',
    mt: 2,
    mb: 2,
  }}>Loading...</Typography>
          ) : response ? (
            <Typography variant="body2" sx={{fontSize: '1.25rem', // or '1.3rem', adjust as needed
              lineHeight: 1.7,
              color: theme => theme.palette.text.secondary,
              textAlign: 'left',
              wordBreak: 'break-word',
              mt: 2,
              mb: 2, whiteSpace: 'pre-line' }}>{response}</Typography>
          ) : (
            <Typography variant="body2" color="text.secondary" fontStyle="italic">
              No response available.
            </Typography>
          )
        )}
        {tabs[tab].label === 'Judge' && (
          judgeScores ? (
            <JudgeSummary scores={judgeScores} />
          ) : (
            <Typography variant="body2" color="text.secondary" fontStyle="italic">
              Judge evaluation not available yet.
            </Typography>
          )
        )}
        {tabs[tab].label === 'Evaluation' && (
          evaluationScores ? (
            <ScoreBreakdown scores={evaluationScores} />
          ) : (
            <Typography variant="body2" color="text.secondary" fontStyle="italic">
              Evaluation metrics not available yet.
            </Typography>
          )
        )}
      </Box>
    </Box>
  );
};

export default ModelResponseTabs;