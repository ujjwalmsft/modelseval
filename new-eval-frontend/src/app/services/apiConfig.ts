/**
 * API configuration for the LLM Models Evaluation application.
 * Defines API endpoints and base URL for all service calls.
 */

// API configuration
export const apiConfig = {
    baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
    endpoints: {
      modelCompare: '/api/compare/compare',
      userHistory: '/api/user/history',
      // contextCompare: '/api/models/compare/context',
      // contextCompare: '/api/models/with-context',
      // contextFileCompare: '/api/models/compare/context-file'
      // contextFileCompare: '/api/models/with-file-context',
    }
  };