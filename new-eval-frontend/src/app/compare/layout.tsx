/**
 * Layout component of compare for the LLM comparison application.
 * 
 * Provides the core application structure with theme management and navigation.
 * Implements responsive design with Material UI components and dynamic theming.
 * Includes user authentication state handling and navigation controls.
 * Features dark/light mode toggle with system preference detection.
 * Maintains consistent layout with header, content area, and footer elements.
 */

'use client';

import React, { useState } from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Container, 
  Box, 
  CssBaseline, 
  ThemeProvider, 
  createTheme,
  useMediaQuery,
  IconButton,
  Button,
  CircularProgress
} from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import CompareIcon from '@mui/icons-material/Compare';
import LogoutIcon from '@mui/icons-material/Logout';
import HomeIcon from '@mui/icons-material/Home';
import { useRouter } from 'next/navigation';
import { useAuth } from '../auth/authContext';
import Header from '../components/Header';
export default function CompareLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  const [mode, setMode] = useState<'light' | 'dark'>(
    prefersDarkMode ? 'dark' : 'light'
  );
  const { isAuthenticated, logout, loading, error } = useAuth();
  const router = useRouter();

  const theme = React.useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: {
            main: mode === 'light' ? '#1976d2' : '#90caf9',
          },
          secondary: {
            main: mode === 'light' ? '#9c27b0' : '#ce93d8',
          },
        },
        typography: {
          fontFamily: '"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        },
      }),
    [mode]
  );

  const toggleColorMode = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  const handleSignOut = async () => {
    await logout();
    router.push('/'); // Redirect to home page after logout
  };

  const goToHome = () => {
    router.push('/');
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header mode={mode} toggleColorMode={toggleColorMode} />
        
        {/* Error message display */}
        {error && (
          <Box 
            sx={{ 
              position: 'sticky',
              top: 64, 
              width: '100%', 
              bgcolor: 'error.main',
              color: 'white',
              p: 1,
              textAlign: 'center',
              zIndex: 1100
            }}
          >
            {error}
          </Box>
        )}

        <Container 
          maxWidth="xl" 
          sx={{ 
            mt: 4, 
            mb: 4, 
            flex: 1,
            borderRadius: 2,
            p: { xs: 2, sm: 3, md: 4 },
            mx: 'auto',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            '& > *': {
              maxWidth: '100%',
            }
          }}
        >
          {children}
        </Container>
        <Box component="footer" sx={{ 
          py: 3, 
          px: 2, 
          mt: 'auto',
          borderTop: 1,
          borderColor: 'divider',
        }}>
          <Typography variant="body2" color="text.secondary" align="center">
           GenAI LLM Evaluator Demo
          </Typography>
        </Box>
      </Box>
    </ThemeProvider>
  );
}