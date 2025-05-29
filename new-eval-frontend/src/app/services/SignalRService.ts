/**
* SignalRService.ts
*
* Manages SignalR real-time connections using Azure SignalR Service.
*/
 
import * as signalR from '@microsoft/signalr';
import { HttpTransportType } from '@microsoft/signalr'; // Add this import

import axios from 'axios';
 
// Judge result structure
export interface JudgeResult {
  model_id: string;
  scores: Record<string, number>;
  reasons: Record<string, string>;
  raw_text?: string;
  duration?: number;
}
 
// Evaluation result structure
export interface EvaluationResult {
  model_id: string;
  BLEU?: number;
  ROUGE_1?: number;
  ROUGE_L?: number;
  BERTScore?: number;
  CosineSimilarity?: number;
  duration?: number;
}
 
// Callback type definitions
type JudgeCallback = (result: JudgeResult) => void;
type EvaluationCallback = (result: EvaluationResult) => void;
 
class SignalRService {
  private connection: signalR.HubConnection | null = null;
  private judgeCallbacks: JudgeCallback[] = [];
  private evaluationCallbacks: EvaluationCallback[] = [];
  private negotiationUrl: string;
  private retryCount = 0;
  private maxRetryDelay = 30000; // 30 seconds maximum delay
  private maxReconnectAttempts = 5;
  
  constructor(negotiationUrl: string) {
    this.negotiationUrl = negotiationUrl;
  }
 
  /**
   * Get connection details from backend negotiation endpoint
   */
  private async getNegotiationDetails(): Promise<{ url: string; accessToken: string }> {
    try {
      console.info('[SignalRService] Starting negotiation...');
      const negotiateEndpoint = `${this.negotiationUrl}/negotiate`;
      console.info(`[SignalRService] Using negotiation endpoint: ${negotiateEndpoint}`);
      
      const response = await axios.get(negotiateEndpoint);
      const data = response.data;
 
      if (!data.url || !data.accessToken) {
        throw new Error('Negotiation response missing URL or accessToken');
      }
 
      console.info('[SignalRService] Negotiation successful, received Azure SignalR details');
      return { url: data.url, accessToken: data.accessToken };
    } catch (error) {
      console.error('[SignalRService] Negotiation failed:', error);
      throw error;
    }
  }
 
  /**
   * Initializes the SignalR connection with proper Azure SignalR flow
   */
  public async connect(): Promise<void> {
    if (this.connection?.state === signalR.HubConnectionState.Connected) {
      console.warn('[SignalRService] Already connected.');
      return;
    }
    
    if (this.retryCount >= this.maxReconnectAttempts) {
      console.error(`[SignalRService] Maximum reconnection attempts (${this.maxReconnectAttempts}) reached.`);
      return;
    }
 
    try {
      // Get connection details from our backend
      const details = await this.getNegotiationDetails();
      
      // Create new connection to Azure SignalR directly
      this.connection = new signalR.HubConnectionBuilder()
      .withUrl(details.url, {
        accessTokenFactory: () => details.accessToken,
        skipNegotiation: true,
        transport: HttpTransportType.WebSockets,
        // Add logging for the transport
        logger: {
          log: (logLevel, message) => {
            console.log(`[Transport ${logLevel}] ${message}`);
          }
        }
      })
      .configureLogging(signalR.LogLevel.Debug) // Increase log level
      .withAutomaticReconnect([0, 2000, 5000, 10000])
      .build();
      
      // Register event handlers
      this.registerHandlers();
      
      // Start the connection
      console.info('[SignalRService] Starting connection to Azure SignalR...');
      await this.connection.start();
      console.info('[SignalRService] Connected successfully to Azure SignalR.');
      
      // Reset retry count on successful connection
      this.retryCount = 0;
    } catch (error) {
      console.error('[SignalRService] Connection failed:', error);
      
      // Implement exponential backoff with max delay
      this.retryCount++;
      const delay = Math.min(1000 * Math.pow(2, this.retryCount), this.maxRetryDelay);
      
      console.warn(`[SignalRService] Retrying in ${delay}ms (attempt ${this.retryCount} of ${this.maxReconnectAttempts})...`);
      setTimeout(() => this.connect(), delay);
    }
  }
 
  /**
   * Gracefully disconnects the SignalR connection
   */
  public async disconnect(): Promise<void> {
    if (!this.connection || this.connection.state === signalR.HubConnectionState.Disconnected) {
      console.warn('[SignalRService] Already disconnected.');
      return;
    }
 
    try {
      await this.connection.stop();
      console.info('[SignalRService] Disconnected successfully.');
    } catch (error) {
      console.error('[SignalRService] Disconnection error:', error);
    }
  }
 
  /**
   * Registers event handlers for SignalR messages
   */
  private registerHandlers(): void {
    if (!this.connection) {
      console.error('[SignalRService] Cannot register handlers - connection not initialized');
      return;
    }
    
    this.connection.on('agent.judge', (data: JudgeResult) => {
      console.debug('[SignalRService] Judge event received:', data);
      this.judgeCallbacks.forEach(cb => cb(data));
    });
 
    this.connection.on('agent.evaluator', (data: EvaluationResult) => {
      console.debug('[SignalRService] Evaluator event received:', data);
      this.evaluationCallbacks.forEach(cb => cb(data));
    });
 
    this.connection.onclose((error) => {
      console.warn('[SignalRService] Connection closed:', error);
      if (error && this.retryCount < this.maxReconnectAttempts) {
        console.warn('[SignalRService] Attempting reconnection...');
        this.connect();
      }
    });
 
    this.connection.onreconnecting((error) => {
      console.warn('[SignalRService] Reconnecting:', error);
    });
 
    this.connection.onreconnected((connectionId) => {
      console.info(`[SignalRService] Reconnected: Connection ID ${connectionId}`);
      this.retryCount = 0;
    });
  }

    /**
   * Registers explicit callback for judge results.
   */
  public onJudgeResult(callback: JudgeCallback): () => void {
    this.judgeCallbacks.push(callback);
    console.debug('[SignalRService] JudgeResult callback registered.');
    return () => {
      this.judgeCallbacks = this.judgeCallbacks.filter(cb => cb !== callback);
      console.debug('[SignalRService] JudgeResult callback unsubscribed.');
    };
  }
 
  /**
   * Registers explicit callback for evaluation results.
   */
  public onEvaluationResult(callback: EvaluationCallback): () => void {
    this.evaluationCallbacks.push(callback);
    console.debug('[SignalRService] EvaluationResult callback registered.');
    return () => {
      this.evaluationCallbacks = this.evaluationCallbacks.filter(cb => cb !== callback);
      console.debug('[SignalRService] EvaluationResult callback unsubscribed.');
    };
  }
 
  /**
   * Clears all explicitly registered callbacks.
   */  
  public clearCallbacks(): void {
    this.judgeCallbacks = [];
    this.evaluationCallbacks = [];
    console.info('[SignalRService] All callbacks cleared.');
  }
}
 
// Export singleton instance
export const signalRService = new SignalRService(
  process.env.NEXT_PUBLIC_SIGNALR_NEGOTIATION_ENDPOINT || 'http://localhost:8000/api/signalr'
);