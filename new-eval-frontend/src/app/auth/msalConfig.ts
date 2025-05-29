/**
 * Microsoft Authentication Library (MSAL) configuration for Azure AD authentication.
 * Defines auth parameters, redirect URIs, and token cache settings.
 */

import { Configuration } from '@azure/msal-browser';

console.log('MSAL Configuration:', process.env.NEXT_PUBLIC_MSAL_CLIENT_ID, process.env.NEXT_PUBLIC_MSAL_TENANT_ID);

// Configuration for MSAL using environment variables
export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_MSAL_CLIENT_ID || '',
    authority: `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_MSAL_TENANT_ID}`,
    redirectUri: typeof window !== 'undefined' ? window.location.origin : '/',
    postLogoutRedirectUri: typeof window !== 'undefined' ? window.location.origin : '/'
  },
  cache: {
    cacheLocation: 'localStorage',
    storeAuthStateInCookie: false
  }
};

// Define authentication scopes
export const authScopes = {
  scopes: [`api://${process.env.NEXT_PUBLIC_MSAL_CLIENT_ID}/User.Read`]
};