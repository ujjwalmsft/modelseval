import React, { useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Typography,
  Skeleton,
  Avatar,
  Divider,
  useTheme,
} from '@mui/material';
import RunMetadata from './RunMetadata';
import ModelResponseTabs from './ModelResponseTabs';

const MODEL_STYLES = {
  gpt4: { color: '#10a37f', icon: '🧠', lightBg: 'rgba(16,163,127,0.05)', darkBg: 'rgba(16,163,127,0.15)' },
  claude3: { color: '#7963d2', icon: '🔮', lightBg: 'rgba(121,99,210,0.05)', darkBg: 'rgba(121,99,210,0.15)' },
  gemini: { color: '#4285f4', icon: '🌐', lightBg: 'rgba(66,133,244,0.05)', darkBg: 'rgba(66,133,244,0.15)' },
  o1mini: { color: '#9c55f5', icon: '⚡', lightBg: 'rgba(156,85,245,0.05)', darkBg: 'rgba(156,85,245,0.15)' },
  deepseek: { color: '#ff6b6b', icon: '🔍', lightBg: 'rgba(255,107,107,0.05)', darkBg: 'rgba(255,107,107,0.15)' },
  phi4: { color: '#00abcc', icon: '🧠', lightBg: 'rgba(0,171,204,0.05)', darkBg: 'rgba(0,171,204,0.15)' },
  llama: { color: '#ff9e43', icon: '🦙', lightBg: 'rgba(255,158,67,0.05)', darkBg: 'rgba(255,158,67,0.15)' },
  gpt4nano: { color: '#0ea47f', icon: '⚡', lightBg: 'rgba(14,164,127,0.05)', darkBg: 'rgba(14,164,127,0.15)' },
};

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

interface ModelResponseCardProps {
  modelId: string;
  modelName: string;
  provider: string;
  response?: string;
  metrics?: {
    responseTime?: number;
    promptTokens?: number;
    completionTokens?: number;
    totalTokens?: number;
    BLEU?: number;
    ROUGE_1?: number;
    ROUGE_L?: number;
    BERTScore?: number;
    CosineSimilarity?: number;
    judgeScores?: JudgeScores;
    evaluation?: EvaluationScores;
    judge?: { metrics?: { judgeScores?: JudgeScores } };
    timestamp?: string;
  };
  loading?: boolean;
  compact?: boolean;
  agentResultsAvailable?: boolean;
}

const ModelResponseCard: React.FC<ModelResponseCardProps> = ({
  modelId,
  modelName,
  provider,
  response,
  metrics,
  loading = false,
  compact = false,
  agentResultsAvailable = false,
}) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === 'dark';
  const modelStyle = MODEL_STYLES[modelId as keyof typeof MODEL_STYLES] || {
    color: '#757575',
    icon: '🤖',
    lightBg: 'rgba(200,200,200,0.1)',
    darkBg: 'rgba(200,200,200,0.05)',
  };
  const bgColor = isDarkMode ? modelStyle.darkBg : modelStyle.lightBg;

  useEffect(() => {
    console.debug(`[ModelResponseCard] Loaded card for model: ${modelName} (ID: ${modelId})`);
  }, [modelId, modelName]);

  const judgeScores: JudgeScores | undefined =
    metrics?.judge?.metrics?.judgeScores || metrics?.judgeScores;
  const evaluationScores: EvaluationScores | undefined =
    metrics?.evaluation || {
      BLEU: metrics?.BLEU,
      ROUGE_1: metrics?.ROUGE_1,
      ROUGE_L: metrics?.ROUGE_L,
      BERTScore: metrics?.BERTScore,
      CosineSimilarity: metrics?.CosineSimilarity,
    };

  return (
    <Card
      raised={!compact}
      sx={{
        height: '100%',
        minHeight: 350,
        display: 'flex',
        flexDirection: 'column',
        transition: 'all 0.3s ease',
        boxShadow: compact ? 1 : 3,
        borderLeft: `4px solid ${modelStyle.color}`,
        '&:hover': {
          boxShadow: compact ? 2 : 4,
        },
        width: '100%',
      }}
    >
      <CardHeader
        avatar={
          <Avatar
            sx={{
              bgcolor: modelStyle.color,
              color: 'white',
              fontWeight: 'bold',
              boxShadow: '0px 2px 4px rgba(0,0,0,0.2)',
            }}
          >
            {modelStyle.icon}
          </Avatar>
        }
        title={
          <Typography variant="h6" fontWeight={600}>
            {modelName}
          </Typography>
        }
        subheader={provider}
        action={
          metrics?.responseTime && !loading && (
            <Chip
              label={`${metrics.responseTime.toFixed(2)}s`}
              size="small"
              sx={{ bgcolor: bgColor, color: modelStyle.color }}
            />
          )
        }
        sx={{ pb: 0, bgcolor: bgColor }}
      />

      <CardContent
        sx={{
          flexGrow: 1,
          pt: 1,
          pb: compact ? 1 : 2,
          px: compact ? 2 : 3,
          overflow: 'auto',
          minHeight: 0,
        }}
      >
        {loading ? (
          <>
            <Skeleton animation="wave" height={20} width="90%" />
            <Skeleton animation="wave" height={20} width="85%" />
            <Skeleton animation="wave" height={20} width="95%" />
            <Skeleton animation="wave" height={20} width="80%" />
          </>
        ) : (
          <ModelResponseTabs
            response={response}
            judgeScores={judgeScores}
            evaluationScores={evaluationScores}
            loading={loading}
            agentResultsAvailable={agentResultsAvailable}
          />
        )}
      </CardContent>

      {!compact && metrics && !loading && (
        <>
          <Divider />
          <Box sx={{ p: 2, bgcolor: bgColor, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {/* {metrics.promptTokens && <Chip label={`${metrics.promptTokens} prompt tokens`} size="small" />}
            {metrics.completionTokens && <Chip label={`${metrics.completionTokens} completion tokens`} size="small" />}
            {metrics.totalTokens && <Chip label={`${metrics.totalTokens} total tokens`} size="small" />} */}

            <RunMetadata
              responseTime={metrics.responseTime}
              promptTokens={metrics.promptTokens}
              completionTokens={metrics.completionTokens}
              totalTokens={metrics.totalTokens}
              timestamp={metrics.timestamp}
            />
          </Box>
        </>
      )}
    </Card>
  );
};

export default ModelResponseCard;