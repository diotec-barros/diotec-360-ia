/**
 * DIOTEC 360 IA - Sovereign SDK
 * 
 * "Integrity as a Service"
 * 
 * Official TypeScript/JavaScript SDK for integrating
 * mathematical proof verification into any application.
 * 
 * @version 1.0.0
 * @license MIT
 */

export interface Diotec360Config {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
}

export interface VerifyRequest {
  intent: string;
  params: Record<string, any>;
}

export interface VerifyResponse {
  verified: boolean;
  merkleProof?: string;
  certificateUrl?: string;
  z3Proof?: string;
  error?: string;
  timestamp?: number;
}

export interface Intent {
  name: string;
  category: string;
  description: string;
  params: Record<string, string>;
}

export class Diotec360SDK {
  private apiKey: string;
  private baseUrl: string;
  private timeout: number;

  constructor(config: Diotec360Config) {
    this.apiKey = config.apiKey;
    this.baseUrl = config.baseUrl || 'https://api.diotec360.com';
    this.timeout = config.timeout || 30000;
  }

  /**
   * Verify an intent with mathematical proof
   */
  async verify(request: VerifyRequest): Promise<VerifyResponse> {
    const response = await fetch(`${this.baseUrl}/api/sdk/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey,
      },
      body: JSON.stringify(request),
      signal: AbortSignal.timeout(this.timeout),
    });

    if (!response.ok) {
      throw new Error(`SDK Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * List all available intents
   */
  async listIntents(): Promise<Intent[]> {
    const response = await fetch(`${this.baseUrl}/api/sdk/intents`, {
      headers: {
        'X-API-Key': this.apiKey,
      },
    });

    if (!response.ok) {
      throw new Error(`SDK Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Health check
   */
  async health(): Promise<{ status: string; version: string }> {
    const response = await fetch(`${this.baseUrl}/api/sdk/health`);
    return response.json();
  }

  /**
   * Verify a financial transfer
   */
  async verifyTransfer(params: {
    from: string;
    to: string;
    amount: number;
    currency: string;
    balance: number;
  }): Promise<VerifyResponse> {
    return this.verify({
      intent: 'transfer',
      params,
    });
  }

  /**
   * Verify an escrow transaction
   */
  async verifyEscrow(params: {
    buyer: string;
    seller: string;
    arbiter: string;
    amount: number;
    currency: string;
  }): Promise<VerifyResponse> {
    return this.verify({
      intent: 'escrow',
      params,
    });
  }

  /**
   * Verify a multi-signature authorization
   */
  async verifyMultisig(params: {
    signers: string[];
    threshold: number;
    signed: string[];
  }): Promise<VerifyResponse> {
    return this.verify({
      intent: 'multisig',
      params,
    });
  }

  /**
   * Verify a loan calculation
   */
  async verifyLoan(params: {
    principal: number;
    rate: number;
    term: number;
    currency: string;
  }): Promise<VerifyResponse> {
    return this.verify({
      intent: 'loan',
      params,
    });
  }

  /**
   * Verify a voting action
   */
  async verifyVote(params: {
    voter_id: string;
    proposal_id: string;
    vote: string;
    voted_before: boolean;
  }): Promise<VerifyResponse> {
    return this.verify({
      intent: 'vote',
      params,
    });
  }

  /**
   * Verify a delivery confirmation
   */
  async verifyDelivery(params: {
    package_id: string;
    gps_lat: number;
    gps_lon: number;
    target_lat: number;
    target_lon: number;
    tolerance_meters: number;
  }): Promise<VerifyResponse> {
    return this.verify({
      intent: 'delivery',
      params,
    });
  }
}

/**
 * Create SDK instance
 */
export function createDiotec360SDK(config: Diotec360Config): Diotec360SDK {
  return new Diotec360SDK(config);
}

// Default export
export default Diotec360SDK;
