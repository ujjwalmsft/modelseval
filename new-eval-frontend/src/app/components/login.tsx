/**
 * Authentication button component that adapts based on user state.
 * 
 * Renders a sign-in or sign-out button depending on authentication status.
 * Displays loading indicator during authentication state transitions.
 * Uses Material UI components with consistent styling and rounded corners.
 * Integrates with the application's auth context for state management.
 */

'use client';

import React from 'react';
import { Button, CircularProgress } from '@mui/material';
import { useAuth } from '../auth/authContext';

const LoginButton: React.FC = () => {
  const { isAuthenticated, login, logout, loading } = useAuth();
  
  if (loading) {
    return <CircularProgress size={24} />;
  }
  
  if (isAuthenticated) {
    return (
      <Button 
        variant="outlined"
        onClick={logout}
        sx={{ borderRadius: 2 }}
      >
        Sign Out
      </Button>
    );
  }
  
  return (
    <Button 
      variant="outlined"
      onClick={login}
      sx={{ borderRadius: 2 }}
    >
      Sign In
    </Button>
  );
};

export default LoginButton;