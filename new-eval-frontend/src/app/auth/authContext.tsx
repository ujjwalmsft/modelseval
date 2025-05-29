/**
 * Authentication context provider for Microsoft Azure AD integration.
 * 
 * Manages the entire authentication lifecycle including:
 * - User login/logout with MSAL popup flow
 * - Token acquisition and management
 * - User profile information extraction from JWT tokens
 * - Persistent authentication state with localStorage
 * - Automatic login detection on app initialization
 * - Comprehensive error handling during authentication operations
 */



'use client';

import { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { PublicClientApplication, AuthenticationResult } from '@azure/msal-browser';
import { msalConfig, authScopes } from './msalConfig';
import { apiConfig } from '../services/apiConfig';
// Import jwt-decode if wanting to use the library
// import jwtDecode from 'jwt-decode';

interface UserInfo {
  name?: string;
  username?: string;
  email?: string;
  preferred_username?: string;
  picture?: string;
  oid?: string; // Object ID in Azure AD
}

interface AuthContextType {
  isAuthenticated: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
  error: string | null;
  token: string | null;
  userInfo: UserInfo | null; // Add user info to the context
  getToken: () => Promise<string | null>;
}

// Create MSAL instance outside the component to ensure it's only created once
const msalInstance = new PublicClientApplication(msalConfig);

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  login: async () => {},
  logout: async () => {},
  loading: true,
  error: null,
  token: null,
  userInfo: null,
  getToken: async () => null
});


// Function to decode JWT token
function parseJwt(token: string): any {
  try {
    // Split the token and get the payload part
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    console.error("Error parsing JWT token:", e);
    return null;
  }
}

interface AuthProviderProps {
  children: ReactNode;
}


export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [initialized, setInitialized] = useState<boolean>(false);
  
  const getToken = async (): Promise<string | null> => {
    // If we already have a token, return it
    if (token) {
      return token;
    }
    
    // If not authenticated or not initialized, return null
    if (!isAuthenticated || !initialized) {
      return null;
    }
    
    // Try to get a fresh token
    try {
      const accounts = msalInstance.getAllAccounts();
      if (accounts.length > 0) {
        const response = await msalInstance.acquireTokenSilent({
          scopes: authScopes.scopes,
          account: accounts[0]
        });
        
        setToken(response.accessToken);
        return response.accessToken;
      }
      return null;
    } catch (err) {
      console.error("Failed to acquire token:", err);
      return null;
    }
  };


  const extractUserInfo = (accessToken: string) => {
    const decodedToken = parseJwt(accessToken);
    if (decodedToken) {
      // The exact properties depend on your Azure AD configuration
      setUserInfo({
        name: decodedToken.name,
        username: decodedToken.preferred_username,
        email: decodedToken.email || decodedToken.preferred_username,
        preferred_username: decodedToken.preferred_username,
        picture: decodedToken.picture,
        oid: decodedToken.oid
      });
    }
  };
// Add this helper function to save user info to localStorage
const saveUserInfoToLocalStorage = (accessToken: string, userInfo: UserInfo | null) => {
  if (typeof window !== 'undefined' && userInfo) {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('user', userInfo.name || '');
    localStorage.setItem('userEmail', userInfo.email || '');
    // localStorage.setItem('userRoles', JSON.stringify(userRoles));
    
    // Store a session ID
    localStorage.setItem('sessionId', `_${Math.random().toString(36).substr(2, 9)}`);
  }
};

// Login function
const login = async () => {
  if (!initialized) {
    setError("Authentication system is still initializing. Please try again.");
    return;
  }
  
  setLoading(true);
  setError(null);
  
  try {
    const response = await msalInstance.loginPopup({
      scopes: authScopes.scopes,
      prompt: 'select_account'
    });
    
    if (response) {
      setToken(response.accessToken);
      setIsAuthenticated(true);
      extractUserInfo(response.accessToken);
      
      // Parse the JWT to get user info
      const userInfo = parseJwt(response.accessToken);
      
      // Save to localStorage
      saveUserInfoToLocalStorage(response.accessToken, {
        name: userInfo.name,
        username: userInfo.preferred_username,
        email: userInfo.email || userInfo.preferred_username,
        preferred_username: userInfo.preferred_username,
        picture: userInfo.picture,
        oid: userInfo.oid
      });
    }
  } catch (err) {
    console.error("Login error:", err);
    setError("Failed to sign in. Please try again.");
  } finally {
    setLoading(false);
  }
};

// MSAL initialization 
useEffect(() => {
  const initializeMsal = async () => {
    try {
      await msalInstance.initialize();
      
      // Check if user is already signed in
      const accounts = msalInstance.getAllAccounts();
      if (accounts.length > 0) {
        try {
          const response = await msalInstance.acquireTokenSilent({
            scopes: authScopes.scopes,
            account: accounts[0]
          });
          
          setToken(response.accessToken);
          setIsAuthenticated(true);
          extractUserInfo(response.accessToken);
          
          // Also save to localStorage here for consistency
          const userInfo = parseJwt(response.accessToken);
          saveUserInfoToLocalStorage(response.accessToken, {
            name: userInfo.name,
            username: userInfo.preferred_username,
            email: userInfo.email || userInfo.preferred_username,
            preferred_username: userInfo.preferred_username,
            picture: userInfo.picture,
            oid: userInfo.oid
          });
        } catch (silentError) {
          console.log("Silent token acquisition failed, user needs to sign in again");
        }
      }
      
      setInitialized(true);
    } catch (err) {
      console.error("MSAL Initialization Error:", err);
      setError("Failed to initialize authentication. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  initializeMsal();
}, []);

// Logout function
const logout = async () => {
  if (!initialized) {
    return;
  }
  
  setLoading(true);
  
  try {
    // First, perform the standard logout
    await msalInstance.logoutPopup({
      postLogoutRedirectUri: msalConfig.auth.postLogoutRedirectUri,
    });
    
    // Clear all accounts from MSAL cache
    // Using the correct method to clear accounts in newer versions of MSAL
    const accounts = msalInstance.getAllAccounts();
    if (accounts.length > 0) {
      // Clear the active account (this is the proper way in current MSAL versions)
      msalInstance.setActiveAccount(null);
    }
    
    // Clear browser storage manually for MSAL-related items
    if (typeof window !== 'undefined') {
      const msalKeys = Object.keys(localStorage).filter(key => 
        key.startsWith('msal.') || 
        key.includes('authority') || 
        key.includes('client.info') ||
        key.includes('idtoken')
      );
      
      msalKeys.forEach(key => {
        localStorage.removeItem(key);
      });
    }

      // Clear custom auth items from local storage
  const customAuthItems = [
    'accessToken',
    'sessionId',
    'user',
    'userEmail',
    'userRoles'
  ];
  customAuthItems.forEach(key => {
    localStorage.removeItem(key);
  });
    // Update state
    setIsAuthenticated(false);
    setToken(null);
    setUserInfo(null);
  } catch (err) {
    console.error("Logout error:", err);
  } finally {
    setLoading(false);
  }
};

  return (
    <AuthContext.Provider value={{ 
      isAuthenticated, 
      login, 
      logout, 
      loading, 
      error, 
      token,
      userInfo,
      getToken // Provide user info 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);