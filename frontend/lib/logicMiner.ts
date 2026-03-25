/**
 * Logic Miner - v4.0.0
 * 
 * Background proof mining system that solves Z3 challenges
 * and earns credits automatically when user is idle.
 * 
 * Architecture:
 * 1. Detect when user is idle (30s without activity)
 * 2. Request Z3 challenge from backend
 * 3. Solve using Z3 (browser-based)
 * 4. Submit proof to backend
 * 5. Earn credits automatically
 * 
 * Result: Gamification + passive income for users
 */

export interface Challenge {
  challenge_id: string;
  z3_formula: string;
  difficulty: number;
  reward_credits: number;
  expires_at: number;
}

export interface MiningState {
  isActive: boolean;
  isMining: boolean;
  currentChallenge: Challenge | null;
  totalProofsSolved: number;
  totalCreditsEarned: number;
  lastMiningTimestamp: number;
  consecutiveFailures: number;
  lastError: string | null;
}

export interface ProofSubmission {
  challenge_id: string;
  proof: string;
  solver_time_ms: number;
  user_public_key: string;
}

export interface ProofResult {
  verified: boolean;
  credits_earned: number;
  total_credits: number;
  merkle_root: string;
}

export type MiningEventType = 'started' | 'stopped' | 'challenge_received' | 'proof_solved' | 'credits_earned' | 'error';

export interface MiningEvent {
  type: MiningEventType;
  data?: any;
}

export type MiningEventCallback = (event: MiningEvent) => void;

export class LogicMiner {
  private state: MiningState;
  private miningLoop: number | null = null;
  private idleTimer: number | null = null;
  private callbacks: MiningEventCallback[] = [];
  private idleThreshold: number = 30000; // 30 seconds
  private lastActivity: number = Date.now();

  constructor() {
    this.state = {
      isActive: false,
      isMining: false,
      currentChallenge: null,
      totalProofsSolved: 0,
      totalCreditsEarned: 0,
      lastMiningTimestamp: 0,
      consecutiveFailures: 0,
      lastError: null
    };

    // Load state from localStorage
    this.loadState();

    // Setup activity detection
    this.setupActivityDetection();
  }

  /**
   * Start mining (enable auto-mining when idle)
   */
  public startMining(): void {
    if (this.state.isActive) {
      console.log('[LogicMiner] Mining already active');
      return;
    }

    this.state.isActive = true;
    this.state.lastError = null;
    this.saveState();
    
    this.notifyEvent({ type: 'started' });
    console.log('[LogicMiner] Mining started - will mine when idle');

    // Start idle detection
    this.startIdleDetection();
  }

  /**
   * Stop mining
   */
  public stopMining(): void {
    if (!this.state.isActive) {
      return;
    }

    this.state.isActive = false;
    this.state.isMining = false;
    this.state.currentChallenge = null;
    this.saveState();

    if (this.miningLoop) {
      clearTimeout(this.miningLoop);
      this.miningLoop = null;
    }

    if (this.idleTimer) {
      clearTimeout(this.idleTimer);
      this.idleTimer = null;
    }

    this.notifyEvent({ type: 'stopped' });
    console.log('[LogicMiner] Mining stopped');
  }

  /**
   * Get current mining state
   */
  public getState(): Readonly<MiningState> {
    return { ...this.state };
  }

  /**
   * Subscribe to mining events
   */
  public onMiningEvent(callback: MiningEventCallback): () => void {
    this.callbacks.push(callback);

    return () => {
      const index = this.callbacks.indexOf(callback);
      if (index >= 0) {
        this.callbacks.splice(index, 1);
      }
    };
  }

  /**
   * Setup activity detection
   */
  private setupActivityDetection(): void {
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];

    const handleActivity = () => {
      this.lastActivity = Date.now();
      
      // If mining, stop it (user is active)
      if (this.state.isMining) {
        console.log('[LogicMiner] User active, pausing mining');
        this.state.isMining = false;
        if (this.miningLoop) {
          clearTimeout(this.miningLoop);
          this.miningLoop = null;
        }
      }
    };

    events.forEach(event => {
      window.addEventListener(event, handleActivity, { passive: true });
    });
  }

  /**
   * Start idle detection
   */
  private startIdleDetection(): void {
    const checkIdle = () => {
      if (!this.state.isActive) {
        return;
      }

      const idleTime = Date.now() - this.lastActivity;

      if (idleTime >= this.idleThreshold && !this.state.isMining) {
        // User is idle, start mining
        console.log('[LogicMiner] User idle, starting mining');
        this.state.isMining = true;
        this.runMiningLoop();
      }

      // Check again in 5 seconds
      this.idleTimer = window.setTimeout(checkIdle, 5000);
    };

    checkIdle();
  }

  /**
   * Main mining loop
   */
  private async runMiningLoop(): Promise<void> {
    if (!this.state.isActive || !this.state.isMining) {
      return;
    }

    try {
      // Step 1: Request challenge from backend
      const challenge = await this.requestChallenge();
      
      if (!challenge) {
        // No challenges available, wait and retry
        this.scheduleMiningLoop(10000); // 10 seconds
        return;
      }

      this.state.currentChallenge = challenge;
      this.notifyEvent({ 
        type: 'challenge_received', 
        data: { 
          challenge_id: challenge.challenge_id,
          difficulty: challenge.difficulty,
          reward: challenge.reward_credits
        } 
      });

      console.log(`[LogicMiner] Received challenge ${challenge.challenge_id} (difficulty: ${challenge.difficulty}, reward: ${challenge.reward_credits})`);

      // Step 2: Solve challenge (simplified - in production would use Z3 WASM)
      const solverResult = await this.solveChallenge(challenge);
      
      if (!solverResult.success) {
        console.log(`[LogicMiner] Failed to solve challenge: ${solverResult.error}`);
        this.handleMiningError(new Error(solverResult.error || 'Solver failed'));
        this.scheduleMiningLoop(5000); // 5 seconds
        return;
      }

      console.log(`[LogicMiner] Challenge solved in ${solverResult.solverTimeMs}ms`);
      this.notifyEvent({ 
        type: 'proof_solved', 
        data: { challenge_id: challenge.challenge_id } 
      });

      // Step 3: Submit proof to backend
      const proofResult = await this.submitProof(challenge, solverResult);
      
      if (proofResult && proofResult.verified) {
        this.state.totalProofsSolved++;
        this.state.totalCreditsEarned += proofResult.credits_earned;
        this.state.lastMiningTimestamp = Date.now();
        this.state.consecutiveFailures = 0;
        this.saveState();

        console.log(`[LogicMiner] Proof verified! Earned ${proofResult.credits_earned} credits (total: ${proofResult.total_credits})`);
        
        this.notifyEvent({
          type: 'credits_earned',
          data: {
            credits: proofResult.credits_earned,
            total: proofResult.total_credits,
            merkle_root: proofResult.merkle_root
          }
        });
      } else {
        console.log('[LogicMiner] Proof rejected by backend');
        this.handleMiningError(new Error('Proof rejected'));
      }

      // Continue mining if still active and idle
      this.scheduleMiningLoop(1000); // 1 second

    } catch (error) {
      console.log(`[LogicMiner] Mining loop error: ${error}`);
      this.handleMiningError(error as Error);
      this.scheduleMiningLoop(30000); // 30 seconds on error
    }
  }

  /**
   * Schedule next mining loop iteration
   */
  private scheduleMiningLoop(delayMs: number): void {
    if (!this.state.isActive || !this.state.isMining) {
      return;
    }

    this.miningLoop = window.setTimeout(() => {
      this.runMiningLoop();
    }, delayMs);
  }

  /**
   * Request challenge from backend
   */
  private async requestChallenge(): Promise<Challenge | null> {
    try {
      const response = await fetch('/api/lattice/challenge', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          // No challenges available
          return null;
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.ok) {
        return null;
      }

      return {
        challenge_id: data.challenge_id,
        z3_formula: data.z3_formula,
        difficulty: data.difficulty,
        reward_credits: data.reward_credits,
        expires_at: data.expires_at
      };

    } catch (error) {
      console.log(`[LogicMiner] Failed to request challenge: ${error}`);
      return null;
    }
  }

  /**
   * Solve challenge (simplified version)
   * In production, this would use Z3 WASM
   */
  private async solveChallenge(challenge: Challenge): Promise<{
    success: boolean;
    proof: string | null;
    solverTimeMs: number;
    error?: string;
  }> {
    const startTime = Date.now();

    try {
      // Simulate solving (in production, would use Z3 WASM)
      await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 400));

      // For now, generate a mock proof
      const proof = `PROOF_${challenge.challenge_id}_${Date.now()}`;

      return {
        success: true,
        proof,
        solverTimeMs: Date.now() - startTime
      };

    } catch (error) {
      return {
        success: false,
        proof: null,
        solverTimeMs: Date.now() - startTime,
        error: String(error)
      };
    }
  }

  /**
   * Submit proof to backend
   */
  private async submitProof(
    challenge: Challenge, 
    solverResult: { proof: string; solverTimeMs: number }
  ): Promise<ProofResult | null> {
    try {
      const publicKey = localStorage.getItem('diotec360-user-public-key');

      if (!publicKey) {
        throw new Error('Sovereign identity not configured');
      }

      const submission: ProofSubmission = {
        challenge_id: challenge.challenge_id,
        proof: solverResult.proof,
        solver_time_ms: solverResult.solverTimeMs,
        user_public_key: publicKey
      };

      const response = await fetch('/api/lattice/submit-proof', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(submission)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.ok) {
        return null;
      }

      return {
        verified: data.verified,
        credits_earned: data.credits_earned,
        total_credits: data.total_credits,
        merkle_root: data.merkle_root
      };

    } catch (error) {
      console.log(`[LogicMiner] Failed to submit proof: ${error}`);
      return null;
    }
  }

  /**
   * Handle mining error with exponential backoff
   */
  private handleMiningError(error: Error): void {
    this.state.consecutiveFailures++;
    this.state.lastError = error.message;
    this.saveState();

    this.notifyEvent({
      type: 'error',
      data: {
        error: error.message,
        consecutiveFailures: this.state.consecutiveFailures
      }
    });

    // Stop mining after 3 consecutive failures
    if (this.state.consecutiveFailures >= 3) {
      console.log('[LogicMiner] Too many consecutive failures, stopping mining');
      this.stopMining();
    }
  }

  /**
   * Load state from localStorage
   */
  private loadState(): void {
    try {
      const data = localStorage.getItem('diotec360-logic-miner-state');
      if (data) {
        const saved = JSON.parse(data);
        this.state.totalProofsSolved = saved.totalProofsSolved || 0;
        this.state.totalCreditsEarned = saved.totalCreditsEarned || 0;
        this.state.lastMiningTimestamp = saved.lastMiningTimestamp || 0;
      }
    } catch (error) {
      console.error('Failed to load miner state:', error);
    }
  }

  /**
   * Save state to localStorage
   */
  private saveState(): void {
    try {
      const data = {
        totalProofsSolved: this.state.totalProofsSolved,
        totalCreditsEarned: this.state.totalCreditsEarned,
        lastMiningTimestamp: this.state.lastMiningTimestamp
      };
      localStorage.setItem('diotec360-logic-miner-state', JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save miner state:', error);
    }
  }

  /**
   * Notify all subscribers of mining event
   */
  private notifyEvent(event: MiningEvent): void {
    this.callbacks.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error('[LogicMiner] Error in event callback:', error);
      }
    });
  }

  /**
   * Dispose and cleanup
   */
  public dispose(): void {
    this.stopMining();
    this.callbacks = [];
  }
}

// Singleton instance
let minerInstance: LogicMiner | null = null;

export function getMiner(): LogicMiner {
  if (!minerInstance) {
    minerInstance = new LogicMiner();
  }
  return minerInstance;
}
