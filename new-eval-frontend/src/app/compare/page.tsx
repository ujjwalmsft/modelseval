'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Alert,
  useTheme,
  Snackbar
} from '@mui/material';
import CompareIcon from '@mui/icons-material/Compare';
import QueryInput from './components/QueryInput';
import ComparisonView from './components/ComparisonView';
import ContextInput from './components/ContextInput';
import { apiService, CompareRequest } from '../services/ApiService';
import { useModelContext } from '../context/ModelContext';
import { useAuth } from '../auth/authContext';
import { v4 as uuidv4 } from 'uuid';

export default function ComparePage() {
  const theme = useTheme();
  const { token } = useAuth();
  const { selectedModelIds } = useModelContext();

  // Input states
  const [query, setQuery] = useState('');
  const [context, setContext] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('You are a helpful assistant.');

  // Mode state
  const [useContextMode, setUseContextMode] = useState(false);

  // Response states
  const [responses, setResponses] = useState<Record<string, string>>({});
  const [metrics, setMetrics] = useState<Record<string, any>>({});
  const [judgeResults, setJudgeResults] = useState<any>({});
  const [evalResults, setEvalResults] = useState<any>({});

  // UI states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showError, setShowError] = useState(false);

  // Session tracking
  const [sessionId, setSessionId] = useState('');
  const [threadId, setThreadId] = useState('');

  // Track if agent results have been fetched
  const [agentResultsFetched, setAgentResultsFetched] = useState(false);

  // Fetch agent results ONCE after LLM responses are loaded (not before)
  useEffect(() => {
    if (
      !sessionId ||
      !threadId ||
      Object.keys(responses).length === 0 ||
      agentResultsFetched
    ) return;

    const fetchAgentResults = async () => {
      try {
        const agentResults = await apiService.getAgentResults(sessionId, threadId);
        if (agentResults.judge) setJudgeResults(agentResults.judge);
        if (agentResults.evaluator) setEvalResults(agentResults.evaluator);
        setAgentResultsFetched(true);
        console.debug('[AgentResults] Judge:', agentResults.judge);
        console.debug('[AgentResults] Evaluator:', agentResults.evaluator);
      } catch (err) {
        console.warn('[AgentResults] Fetch failed:', err);
      }
    };

    fetchAgentResults();
  }, [sessionId, threadId, responses, agentResultsFetched]);

  const handleSubmit = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      setShowError(true);
      return;
    }

    if (useContextMode && !context.trim()) {
      setError('Context is required when using Context-Aware mode');
      setShowError(true);
      return;
    }

    if (!selectedModelIds || selectedModelIds.length === 0) {
      setError('Please select at least one model');
      setShowError(true);
      return;
    }

    setLoading(true);
    setResponses({});
    setMetrics({});
    setJudgeResults({});
    setEvalResults({});
    setAgentResultsFetched(false);
    setError('');

    const newSessionId = `session-${uuidv4().substring(0, 8)}`;
    const newThreadId = `thread-${uuidv4().substring(0, 8)}`;

    setSessionId(newSessionId);
    setThreadId(newThreadId);

    const request: CompareRequest = {
      prompt: query,
      models: selectedModelIds,
      system_prompt: systemPrompt,
      session_id: newSessionId,
      mcp_thread_id: newThreadId,
      use_case_id: useContextMode ? '2' : '1',
      context: context
    };

    try {
      const result = await apiService.compareModels(request, token);

      const modelResponses: Record<string, string> = {};
      const modelMetrics: Record<string, any> = {};

      if (result.responses) {
        Object.entries(result.responses).forEach(([modelId, response]) => {
          modelResponses[modelId] = (response as any).content;
          modelMetrics[modelId] = (response as any).metrics;
        });
      }

      setResponses(modelResponses);
      setMetrics(modelMetrics);
      console.debug('[ComparePage] Model responses:', modelResponses);
      console.debug('[ComparePage] Model metrics:', modelMetrics);
    } catch (err) {
      console.error('[API] Error:', err);
      setError('Failed to compare models.');
      setShowError(true);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseError = () => setShowError(false);

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Paper elevation={0} sx={{
        p: 4, borderRadius: 2, mb: 4,
        backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)',
        border: `1px solid ${theme.palette.divider}`, width: '100%',
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <CompareIcon sx={{ mr: 2, color: theme.palette.primary.main }} />
          <Typography variant="h4" component="h1" fontWeight={600}>
            Compare Models
          </Typography>
        </Box>

        <Typography variant="body1" paragraph color="text.secondary">
          Compare responses from different LLMs for the same query. Evaluate capabilities, accuracy, and appropriateness.
        </Typography>

        {useContextMode && (
          <ContextInput context={context} setContext={setContext} />
        )}

        <QueryInput
          query={query}
          setQuery={setQuery}
          systemPrompt={systemPrompt}
          setSystemPrompt={setSystemPrompt}
          onSubmit={handleSubmit}
          loading={loading}
          useContextMode={useContextMode}
          setUseContextMode={setUseContextMode}
        />
      </Paper>

      <ComparisonView
        responses={responses}
        metrics={metrics}
        loading={loading}
        judgeResults={judgeResults}
        evalResults={evalResults}
        agentResultsAvailable={agentResultsFetched}
      />

      {Object.keys(responses).length > 0 && (
        <Box sx={{ mt: 2 }}>
          {/* Optionally, add run metadata or other session info here */}
        </Box>
      )}

      <Snackbar open={showError} autoHideDuration={6000} onClose={handleCloseError}>
        <Alert severity="error">{error}</Alert>
      </Snackbar>
    </Container>
  );
}