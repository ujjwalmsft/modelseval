
/**
* ComparisonView.tsx
*
* Displays multiple LLM responses side-by-side, incorporating qualitative (judge scores)
* and quantitative (evaluation metrics) results via polling.
*
* Features:
* - Responsive layout with animated transitions (Material UI Slide component).
* - Comprehensive debugging logs for enhanced traceability.
* - Graceful handling of state and model selections with fallback logic.
* - Passes judge and evaluation results to each ModelResponseCard for per-card toggling.
*/


import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Typography,
  Grid,
  useTheme,
  Slide,
} from '@mui/material';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import ModelResponseCard from './ModelResponseCard';
import { useModelContext } from '../../context/ModelContext';

const allAvailableModels = [
  { id: 'gpt4', name: 'GPT-4 Turbo', provider: 'Azure AI Foundry' },
  { id: 'claude3', name: 'Claude 3 Opus', provider: 'Anthropic' },
  { id: 'gemini', name: 'Gemini Pro', provider: 'Google AI' },
  { id: 'o1mini', name: 'O1-mini', provider: 'Azure AI Foundry' },
  { id: 'deepseek', name: 'DeepSeek-R1', provider: 'Azure AI Foundry' },
  { id: 'phi4', name: 'Phi-4', provider: 'Azure AI Foundry' },
  { id: 'llama', name: 'Llama 3', provider: 'Azure AI Foundry' },
  { id: 'gpt4nano', name: 'GPT-4.1-nano', provider: 'Azure AI Foundry' },
];

interface ComparisonViewProps {
  responses: Record<string, string>;
  metrics: Record<string, any>;
  loading: boolean;
  selectedModelIds?: string[];
  judgeResults?: Record<string, any>;
  evalResults?: Record<string, any>;
  agentResultsAvailable?: boolean;
}

const ComparisonView: React.FC<ComparisonViewProps> = ({
  responses,
  metrics: initialMetrics,
  loading,
  selectedModelIds: selectedModelIdsProp,
  judgeResults = {},
  evalResults = {},
  agentResultsAvailable = false,
}) => {
  const theme = useTheme();
  const { selectedModelIds: contextModelIds } = useModelContext();

  const [modelIds, setModelIds] = useState<string[]>([]);

  // Determine selected models explicitly (priority: props → context → localStorage → defaults)
  useEffect(() => {
    const determineModels = (): string[] => {
      if (selectedModelIdsProp?.length) return selectedModelIdsProp;
      if (contextModelIds?.length) return contextModelIds;
      const storedModels = localStorage.getItem('selectedModelIds');
      if (storedModels) {
        try {
          const parsed = JSON.parse(storedModels);
          if (Array.isArray(parsed) && parsed.length > 0) return parsed;
        } catch {}
      }
      return ['gpt4', 'claude3', 'gemini', 'o1mini'];
    };
    setModelIds(determineModels());
  }, [selectedModelIdsProp, contextModelIds]);

  // Update selected models explicitly when context changes
  useEffect(() => {
    if (
      !selectedModelIdsProp &&
      contextModelIds?.length &&
      JSON.stringify(contextModelIds) !== JSON.stringify(modelIds)
    ) {
      setModelIds(contextModelIds);
    }
  }, [contextModelIds, selectedModelIdsProp, modelIds]);

  // Filter explicitly available models
  const availableModels = useMemo(
    () => allAvailableModels.filter((model) => modelIds.includes(model.id)),
    [modelIds]
  );

  const hasResponses = Object.keys(responses).length > 0 || loading;
  const hasActualResponses = Object.keys(responses).length > 0;

  return (
    <Box sx={{ mt: 4 }}>
      {hasResponses && (
        <Typography
          variant="h5"
          sx={{
            mb: 3,
            display: 'flex',
            alignItems: 'center',
            fontWeight: 600,
            color: theme.palette.mode === 'dark' ? '#fff' : '#333',
            '&::after': {
              content: '""',
              display: 'block',
              height: '2px',
              background: theme.palette.primary.main,
              flexGrow: 1,
              ml: 2,
            },
          }}
        >
          <CompareArrowsIcon sx={{ mr: 1, color: theme.palette.primary.main }} />
          Model Responses
        </Typography>
      )}

      <Grid container spacing={3}>
        {availableModels.map((model, index) => (
          <Grid
            key={model.id}
            item
            xs={12}
            sm={hasActualResponses ? 12 : 6}
            md={hasActualResponses ? 12 : 3}
            sx={{ height: 400, display: 'flex', width: '100%' }}
          >
            <Slide
              direction="up"
              in
              style={{ transitionDelay: `${index * 100}ms` }}
            >
              <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
                <ModelResponseCard
                  modelId={model.id}
                  modelName={model.name}
                  provider={model.provider}
                  response={responses[model.id]}
                  metrics={{
                    ...initialMetrics[model.id],
                    judge: judgeResults[model.id],
                    evaluation: evalResults[model.id]?.metrics?.comparison,
                    timestamp: initialMetrics[model.id]?.timestamp,
                  }}
                  loading={loading && !responses[model.id]}
                  compact={!hasActualResponses}
                  agentResultsAvailable={agentResultsAvailable}
                />
              </Box>
            </Slide>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default ComparisonView;