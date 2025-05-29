/**
 * User profile component with dropdown menu for account management.
 * 
 * Displays user information with avatar and name based on authentication state.
 * Provides a dropdown menu with user details, roles, and navigation options.
 * Features contextual sign-in/sign-out buttons with appropriate icons.
 * Implements popup menu with styled appearance and arrow indicator.
 * Adapts display based on screen size for optimal mobile/desktop experience.
 */

'use client';

import { useState } from 'react';
import {
  Box,
  Avatar,
  Typography,
  Button,
  Menu,
  MenuItem,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import LoginIcon from '@mui/icons-material/Login';
import LogoutIcon from '@mui/icons-material/Logout';
import { useAuth } from '../auth/authContext';
import { useRouter } from 'next/navigation';

interface UserProfileProps {
  mode: 'light' | 'dark';
}

const UserProfile: React.FC<UserProfileProps> = ({ mode }) => {
  const { isAuthenticated, login, logout, loading, userInfo } = useAuth();
  const router = useRouter();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  
  // Get user roles from localStorage if available
  const userRoles = typeof window !== 'undefined' ? 
    JSON.parse(localStorage.getItem('userRoles') || '[]') : 
    [];
  
  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleClose = () => {
    setAnchorEl(null);
  };
  
  const handleSignIn = async () => {
    await login();
  };
  
  const handleSignOut = async () => {
    handleClose();
    await logout();
  };
  
  const handleCompare = () => {
    handleClose();
    router.push('/compare');
  };

  if (loading) {
    return null; // Don't show anything during loading
  }
  
  if (!isAuthenticated) {
    return (
      <Button
        variant="outlined"
        onClick={handleSignIn}
        endIcon={<LoginIcon />}
        sx={{ 
          borderRadius: 2,
          textTransform: 'none'
        }}
      >
        Sign In
      </Button>
    );
  }
  
  const userName = userInfo?.name || localStorage.getItem('user') || 'User';
  const userEmail = userInfo?.email || localStorage.getItem('userEmail') || '';
  
  return (
    <Box>
      <Tooltip title="Account settings">
        <Button
          onClick={handleClick}
          sx={{ 
            textTransform: 'none',
            borderRadius: 2,
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            px: 1.5,
            py: 0.5,
            bgcolor: open ? 'action.selected' : 'transparent'
          }}
        >
          <Avatar 
            sx={{ 
              width: 32, 
              height: 32,
              bgcolor: 'primary.main',
              fontSize: '1rem'
            }}
            src={userInfo?.picture}
          >
            {userName.charAt(0).toUpperCase()}
          </Avatar>
          <Typography 
            variant="body2" 
            sx={{ 
              display: { xs: 'none', sm: 'block' },
              fontWeight: 500
            }}
          >
            {userName}
          </Typography>
        </Button>
      </Tooltip>
      
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          elevation: 2,
          sx: {
            minWidth: 200,
            mt: 1.5,
            '& .MuiMenu-list': {
              py: 1
            },
            overflow: 'visible',
            filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.15))',
            '&:before': {
              content: '""',
              display: 'block',
              position: 'absolute',
              top: 0,
              right: 14,
              width: 10,
              height: 10,
              bgcolor: 'background.paper',
              transform: 'translateY(-50%) rotate(45deg)',
              zIndex: 0,
            },
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <Box sx={{ px: 2, py: 1 }}>
          <Typography variant="subtitle1" fontWeight={600}>
            {userName}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {userEmail}
          </Typography>
        </Box>
        
        {userRoles && userRoles.length > 0 && (
          <>
            <Divider />
            <Box sx={{ px: 2, py: 1 }}>
              <Typography variant="body2" fontWeight={500} color="text.secondary">
                Roles
              </Typography>
              {userRoles.map((role: string, index: number) => (
                <Typography key={index} variant="body2">
                  {role}
                </Typography>
              ))}
            </Box>
          </>
        )}
        
        <Divider />
        
        <MenuItem onClick={handleCompare} dense>
          Compare Models
        </MenuItem>
        
        <Divider />
        
        <MenuItem onClick={handleSignOut} dense>
          <LogoutIcon fontSize="small" sx={{ mr: 1 }} />
          Sign out
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default UserProfile;