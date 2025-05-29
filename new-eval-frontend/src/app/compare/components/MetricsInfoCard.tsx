'use client';

import React from 'react';
import { Box, Typography, Card, CardContent, CardHeader, IconButton, Divider, useTheme, Button, Avatar } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

interface MetricInfo {
  name: string;
  shortName?: string;
  icon?: React.ReactNode;
  description: string;
  threshold?: string;
  useCases?: string[];
  moreInfoUrl?: string;
}

interface MetricInfoCardProps {
  open: boolean;
  onClose: () => void;
  metric: MetricInfo;
}

const MetricInfoCard: React.FC<MetricInfoCardProps> = ({ open, onClose, metric }) => {
  const theme = useTheme();

  if (!open) return null;

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        zIndex: 1400,
        width: '100vw',
        height: '100vh',
        bgcolor: 'rgba(0,0,0,0.45)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backdropFilter: 'blur(2px)',
      }}
      onClick={onClose}
    >
      <Card
        sx={{
          minWidth: 420,
          maxWidth: 600,
          width: '95vw',
          minHeight: 420,
          boxShadow: 8,
          borderRadius: 4,
          bgcolor: theme.palette.background.paper,
          position: 'relative',
          overflow: 'visible',
          p: 0,
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Graphic Header */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            bgcolor: theme.palette.primary.main,
            color: theme.palette.primary.contrastText,
            borderTopLeftRadius: 16,
            borderTopRightRadius: 16,
            px: 4,
            py: 3,
            position: 'relative',
            minHeight: 90,
            mb: 1,
          }}
        >
          <Avatar
            sx={{
              bgcolor: theme.palette.background.paper,
              color: theme.palette.primary.main,
              width: 64,
              height: 64,
              mr: 3,
              boxShadow: 2,
              fontSize: 36,
            }}
            variant="rounded"
          >
            {metric.icon}
          </Avatar>
          <Box>
            <Typography variant="h4" fontWeight={800} sx={{ letterSpacing: 1 }}>
              {metric.name}
            </Typography>
            {metric.shortName && (
              <Typography variant="subtitle1" sx={{ opacity: 0.85 }}>
                {metric.shortName}
              </Typography>
            )}
          </Box>
          <IconButton
            onClick={onClose}
            aria-label="close"
            sx={{
              position: 'absolute',
              top: 12,
              right: 12,
              color: theme.palette.primary.contrastText,
              bgcolor: 'rgba(0,0,0,0.08)',
              '&:hover': { bgcolor: 'rgba(0,0,0,0.15)' },
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
        <Divider />
        <CardContent sx={{ px: 5, py: 3 }}>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
            {metric.description}
          </Typography>
          {metric.threshold && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" fontWeight={700}>
                Typical Good Score:
              </Typography>
              <Typography variant="body1" color="primary" fontWeight={600}>
                {metric.threshold}
              </Typography>
            </Box>
          )}
          {metric.useCases && metric.useCases.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" fontWeight={700}>
                Common Use Cases:
              </Typography>
              <ul style={{ margin: 0, paddingLeft: 22 }}>
                {metric.useCases.map((uc, idx) => (
                  <li key={idx}>
                    <Typography variant="body1" color="text.secondary">
                      {uc}
                    </Typography>
                  </li>
                ))}
              </ul>
            </Box>
          )}
          {/* {metric.moreInfoUrl && (
            <Button
              variant="outlined"
              color="primary"
              href={metric.moreInfoUrl}
              target="_blank"
              rel="noopener noreferrer"
              sx={{ mt: 2, fontWeight: 600 }}
            >
              Learn more about {metric.name}
            </Button>
          )} */}
        </CardContent>
      </Card>
    </Box>
  );
};

export default MetricInfoCard;