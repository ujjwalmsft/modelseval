/**
* ApiService.ts
*
* Centralized API service for managing LLM model comparisons, user history retrieval,
* and utility methods for mapping model display names to backend model identifiers.
*
* Features:
* - Supports zero-shot and context-aware model comparison scenarios.
* - Handles authorization headers securely with robust validation.
* - Detailed debug logging for tracing requests and responses.
* - Structured API responses clearly aligned with the backend schema.
* - Graceful handling of errors with clear logging and messaging.
*/
 
import { apiConfig } from './apiConfig';
 
// Comparison modes supported explicitly
export type ComparisonMode = 'direct' | 'context';
 
// Explicit request schema for model comparisons
export interface CompareRequest {
  prompt: string;
  models: string[];
  context?: string;
  use_case_id: '1' | '2'; // 1 = zero-shot, 2 = context-aware
  system_prompt?: string;
  session_id?: string;
  mcp_thread_id?: string;
}
 
// Explicit response schema for model comparisons (aligned with backend updates)
export interface CompareResponse {
  responses: Record<
    string,
    {
      content: string;
      metrics: {
        responseTime: number;
        promptTokens?: number;
        completionTokens?: number;
        totalTokens?: number;
      };
      safety?: any;
      id?: string;
    }
>;
  conversationId?: string;
}
 
// History item schema for user's past queries
export interface HistoryItem {
  id: string;
  prompt: string;
  timestamp: string;
}
 
// Explicit response schema for user's history
interface HistoryResponse {
  history: HistoryItem[];
}
 
class ApiService {
  private baseUrl: string;
 
  constructor() {
    this.baseUrl = apiConfig.baseUrl;
    console.debug(`[ApiService] Initialized with base URL: ${this.baseUrl}`);
  }
 
  /**
   * Generates authorization headers explicitly for API requests.
   * @param token - User authorization token.
   */
  private async getAuthHeader(token: string | null): Promise<HeadersInit> {
    const headers: HeadersInit = { 'Content-Type': 'application/json' };
 
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
      console.debug('[ApiService] Authorization header set.');
    } else {
      console.warn('[ApiService] No authorization token provided.');
    }
 
    return headers;
  }
 
  /**
   * Explicitly submits a model comparison request to the backend.
   * Supports zero-shot and context-aware scenarios.
   * @param request - Payload containing model comparison details.
   * @param token - User authorization token.
   */
  async compareModels(
    request: CompareRequest,
    token: string | null = null
  ): Promise<CompareResponse> {
    const headers = await this.getAuthHeader(token);
 
    // Ensure context is only included explicitly for context-aware mode (use_case_id = '2')
    const finalRequest = {
      ...request,
      context: request.use_case_id === '2' ? request.context || '' : '',
    };
 
    console.debug('[ApiService] Submitting compareModels request:', finalRequest);
 
    const response = await fetch(`${this.baseUrl}${apiConfig.endpoints.modelCompare}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(finalRequest),
    });
 
    if (!response.ok) {
      const errorMessage = `[ApiService] compareModels failed (${response.status}): ${response.statusText}`;
      console.error(errorMessage);
      throw new Error(errorMessage);
    }
 
    const responseData = (await response.json()) as CompareResponse;
    console.debug('[ApiService] Received compareModels response:', responseData);
 
    return responseData;
  }
 
  /**
   * Retrieves the user's past query history explicitly.
   * @param token - User authorization token.
   */
  async getUserHistory(token: string): Promise<HistoryItem[]> {
    const headers = await this.getAuthHeader(token);
 
    console.debug('[ApiService] Requesting user history.');
 
    const response = await fetch(`${this.baseUrl}${apiConfig.endpoints.userHistory}`, {
      method: 'GET',
      headers,
    });
 
    if (!response.ok) {
      const errorMessage = `[ApiService] getUserHistory failed (${response.status}): ${response.statusText}`;
      console.error(errorMessage);
      throw new Error(errorMessage);
    }
 
    const data = (await response.json()) as HistoryResponse;
    console.debug('[ApiService] Received user history:', data);
 
    return data.history;
  }
 
  /**
   * Maps user-friendly model display names explicitly to backend model IDs.
   * @param displayName - Model name as displayed to the user.
   */
  static getModelId(displayName: string): string {
    const modelMap: Record<string, string> = {
      'GPT-4': 'gpt4',
      'Claude 3': 'claude3',
      'Gemini Pro': 'gemini',
      'O1-mini': 'o1mini',
      'DeepSeek-R1': 'deepseek',
      'Phi-4': 'phi4',
      'GPT-4.1-nano': 'gpt4nano',
      'Llama 3': 'llama',
    };
 
    const mappedId =
      modelMap[displayName] || displayName.toLowerCase().replace(/\s+/g, '');
    console.debug(`[ApiService] Model name "${displayName}" mapped to ID "${mappedId}"`);
 
    return mappedId;
  }

  async getAgentResults(sessionId: string, threadId?: string) {
    let url = `${this.baseUrl}/api/${sessionId}`;
    if (threadId) url += `?thread_id=${threadId}`;
    const response = await fetch(url, { method: 'GET' });
    console.log(`[ApiService] Fetching agent results from: ${url}`);
    console.log(response);

    if (!response.ok) throw new Error('Failed to fetch agent results');
    return await response.json();
  }


}
 
// Export singleton instance explicitly
export const apiService = new ApiService();