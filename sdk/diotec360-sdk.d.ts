/**
 * DIOTEC 360 IA - Sovereign SDK Type Definitions
 * @version 1.0.0
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
  constructor(config: Diotec360Config);
  
  verify(request: VerifyRequest): Promise<VerifyResponse>;
  listIntents(): Promise<Intent[]>;
  health(): Promise<{ status: string; version: string }>;
  
  verifyTransfer(params: {
    from: string;
    to: string;
    amount: number;
    currency: string;
    balance: number;
  }): Promise<VerifyResponse>;
  
  verifyEscrow(params: {
    buyer: string;
    seller: string;
    arbiter: string;
    amount: number;
    currency: string;
  }): Promise<VerifyResponse>;
  
  verifyMultisig(params: {
    signers: string[];
    threshold: number;
    signed: string[];
  }): Promise<VerifyResponse>;
  
  verifyLoan(params: {
    principal: number;
    rate: number;
    term: number;
    currency: string;
  }): Promise<VerifyResponse>;
  
  verifyVote(params: {
    voter_id: string;
    proposal_id: string;
    vote: string;
    voted_before: boolean;
  }): Promise<VerifyResponse>;
  
  verifyDelivery(params: {
    package_id: string;
    gps_lat: number;
    gps_lon: number;
    target_lat: number;
    target_lon: number;
    tolerance_meters: number;
  }): Promise<VerifyResponse>;
}

export function createDiotec360SDK(config: Diotec360Config): Diotec360SDK;

export default Diotec360SDK;
