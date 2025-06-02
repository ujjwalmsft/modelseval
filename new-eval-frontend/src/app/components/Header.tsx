/**
 * Application header component with navigation and theme controls.
 * 
 * Provides consistent navigation with conditional home button display.
 * Features user profile information and authentication status indicator.
 * Includes theme toggle functionality between light and dark modes.
 * Implements responsive design with proper spacing for fixed positioning.
 * Uses Material UI components for consistent visual styling and interactions.
 */

'use client';

import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Box,
  useMediaQuery,
  CircularProgress
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import HomeIcon from '@mui/icons-material/Home';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { useRouter, usePathname } from 'next/navigation';
import UserProfile from './UserProfile';

interface HeaderProps {
  mode: 'light' | 'dark';
  toggleColorMode: () => void;
}

const Header: React.FC<HeaderProps> = ({ mode, toggleColorMode }) => {
  const theme = useTheme();
  const router = useRouter();
  const pathname = usePathname();

  // Check if we're on the compare page to conditionally show the home button
  const isComparePage = pathname === '/compare';

  // Function to navigate to home page
  const goToHome = () => {
    router.push('/');
  };

  return (
    <>
      <AppBar position="fixed" color="default" elevation={1} sx={{ bgcolor: 'background.paper' }}>
        <Toolbar>
          <CompareArrowsIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Models Comparison
          </Typography>

          {/* Show Home button only on the compare page */}
          {isComparePage && (
            <Button 
              variant="text" 
              onClick={goToHome} 
              startIcon={<HomeIcon />}
              sx={{ mr: 2 }}
            >
              Home
            </Button>
          )}

          <IconButton onClick={toggleColorMode} color="inherit" sx={{ mr: 1 }}>
            {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
          
          <UserProfile mode={mode} />
        </Toolbar>
      </AppBar>
      <Toolbar /> {/* Spacer for fixed AppBar */}
    </>
  );
};

export default Header;