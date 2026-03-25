/**
 * DIOTEC 360 IA - Dual-Brain Orchestrator (Writer-Critic Architecture)
 * 
 * Inspired by DIOTEC-EDITOR's MoE (Mixture of Experts) system
 * 
 * Architecture:
 * 1. Writer AI generates code (GPT-4, Claude, Ollama)
 * 2. Critic AI reviews for correctness, safety, alignment
 * 3. Judge Z3 validates mathematically
 * 
 * This is a PREMIUM feature ($29/month)
 */

export type ProviderId = 'openai' | 'anthropic' | 'ollama';
export type RiskLevel = 'low' | 'medium' | 'high';

export interface DualBrainConfig {
  enabled: boolean;
  writer: {
    provider: ProviderId;
    model?: string;
  };
  critic: {
    provider: ProviderId;
    model?: string;
    minChars: number;
  };
}

export interface DualBrainResult {
  writerOutput: string;
  criticReview: string;
  criticRisk: RiskLevel | undefined;
  judgeVerdict: 'PROVED' | 'UNSAT' | 'TIMEOUT' | 'ERROR' | undefined;
  z3Proof?: string;
  finalCode: string;
  executionTimeMs: number;
}

export interface LLMMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export class DualBrainOrchestrator {
  private config: DualBrainConfig;

  constructor(config?: Partial<DualBrainConfig>) {
    this.config = {
      enabled: config?.enabled ?? true,
      writer: {
        provider: config?.writer?.provider ?? 'openai',
        model: config?.writer?.model ?? 'gpt-4',
      },
      critic: {
        provider: config?.critic?.provider ?? 'anthropic',
        model: config?.critic?.model ?? 'claude-3-5-sonnet-20241022',
        minChars: config?.critic?.minChars ?? 50,
      },
    };
  }

  isEnabled(): boolean {
    return this.config.enabled;
  }

  updateConfig(config: Partial<DualBrainConfig>): void {
    this.config = { ...this.config, ...config };
  }

  getConfig(): DualBrainConfig {
    return { ...this.config };
  }

  /**
   * Main orchestration method
   * Runs Writer → Critic → Judge in sequence
   */
  async generate(prompt: string, context?: string): Promise<DualBrainResult> {
    const startTime = Date.now();

    try {
      // Step 1: Writer generates code
      const writerOutput = await this.callWriter(prompt, context);

      // Step 2: Critic reviews (if enabled and output is long enough)
      let criticReview = '';
      let criticRisk: RiskLevel | undefined = undefined;

      if (this.shouldRunCritic(writerOutput)) {
        criticReview = await this.callCritic(prompt, writerOutput, context);
        criticRisk = this.parseRiskLevel(criticReview);
      }

      // Step 3: Judge validates (Z3 verification)
      let judgeVerdict: DualBrainResult['judgeVerdict'] = undefined;
      let z3Proof: string | undefined = undefined;

      try {
        const judgeResult = await this.callJudge(writerOutput);
        judgeVerdict = judgeResult.verdict;
        z3Proof = judgeResult.proof;
      } catch (err) {
        console.warn('Judge verification failed:', err);
      }

      // Step 4: Merge results
      const finalCode = this.mergeFeedback(writerOutput, criticReview);

      const executionTimeMs = Date.now() - startTime;

      return {
        writerOutput,
        criticReview,
        criticRisk,
        judgeVerdict,
        z3Proof,
        finalCode,
        executionTimeMs,
      };
    } catch (error) {
      throw new Error(`Dual-Brain generation failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Call Writer AI to generate code
   */
  private async callWriter(prompt: string, context?: string): Promise<string> {
    const messages: LLMMessage[] = [
      {
        role: 'system',
        content: `You are DIOTEC 360 IA Writer. Generate correct, secure, and mathematically provable code.
Rules:
- Write clean, idiomatic code
- Include assertions for Z3 verification
- Follow best practices
- Be concise and practical
- Output code only, no explanations unless asked`,
      },
      {
        role: 'user',
        content: this.buildWriterPrompt(prompt, context),
      },
    ];

    return this.callLLM(this.config.writer.provider, this.config.writer.model, messages);
  }

  /**
   * Call Critic AI to review Writer's output
   */
  private async callCritic(prompt: string, writerOutput: string, context?: string): Promise<string> {
    const messages: LLMMessage[] = [
      {
        role: 'system',
        content: `You are DIOTEC 360 IA Critic. Review the Writer output for correctness, safety, and alignment.
Rules:
- Do NOT rewrite the full solution. Provide review only.
- Be concise and practical.
- Output Markdown.
Return this structure:
## Risk
<low|medium|high>

## Issues
- ...

## Suggestions
- ...`,
      },
      {
        role: 'user',
        content: this.buildCriticPrompt(prompt, writerOutput, context),
      },
    ];

    return this.callLLM(this.config.critic.provider, this.config.critic.model, messages);
  }

  /**
   * Call Judge (Z3) to verify code mathematically
   */
  private async callJudge(code: string): Promise<{ verdict: 'PROVED' | 'UNSAT' | 'TIMEOUT' | 'ERROR'; proof?: string }> {
    try {
      const response = await fetch('/api/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        throw new Error(`Judge API error: ${response.statusText}`);
      }

      const result = await response.json();
      return {
        verdict: result.verdict || 'ERROR',
        proof: result.proof,
      };
    } catch (error) {
      console.error('Judge verification error:', error);
      return { verdict: 'ERROR' };
    }
  }

  /**
   * Call LLM provider (OpenAI, Anthropic, Ollama)
   */
  private async callLLM(provider: ProviderId, model: string | undefined, messages: LLMMessage[]): Promise<string> {
    try {
      // Get user's API keys from localStorage (BYOK)
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      
      if (typeof window !== 'undefined') {
        const savedKeys = localStorage.getItem('diotec360-api-keys');
        if (savedKeys) {
          const keys = JSON.parse(savedKeys);
          
          // Add user's keys to headers (backend will use them if available)
          if (provider === 'openai' && keys.openai) {
            headers['X-User-OpenAI-Key'] = keys.openai;
          } else if (provider === 'anthropic' && keys.anthropic) {
            headers['X-User-Anthropic-Key'] = keys.anthropic;
          } else if (provider === 'ollama' && keys.ollamaUrl) {
            headers['X-User-Ollama-URL'] = keys.ollamaUrl;
          }
        }
      }

      const response = await fetch('/api/llm/generate', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          provider,
          model,
          messages,
        }),
      });

      if (!response.ok) {
        throw new Error(`LLM API error: ${response.statusText}`);
      }

      const result = await response.json();
      return result.content || result.text || '';
    } catch (error) {
      throw new Error(`Failed to call ${provider}: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Build Writer prompt with context
   */
  private buildWriterPrompt(prompt: string, context?: string): string {
    const parts = ['Task:', prompt];

    if (context) {
      parts.push('', 'Context:', '```', context, '```');
    }

    parts.push('', 'Generate code that is correct, secure, and mathematically provable.');

    return parts.join('\n');
  }

  /**
   * Build Critic prompt with Writer output
   */
  private buildCriticPrompt(prompt: string, writerOutput: string, context?: string): string {
    const parts = [
      'Original task:',
      prompt,
      '',
    ];

    if (context) {
      parts.push('Context:', '```', context, '```', '');
    }

    parts.push(
      'Writer output to review:',
      '```',
      writerOutput.trim(),
      '```',
      '',
      'Review for:',
      '- Correctness',
      '- Security vulnerabilities',
      '- Missing edge cases',
      '- Style consistency',
      '- Potential bugs'
    );

    return parts.join('\n');
  }

  /**
   * Merge Writer output with Critic feedback
   */
  private mergeFeedback(writerOutput: string, criticReview: string): string {
    if (!criticReview || criticReview.trim().length === 0) {
      return writerOutput;
    }

    return [
      writerOutput,
      '',
      '---',
      '',
      '## Dual-Brain Review',
      criticReview.trim(),
    ].join('\n');
  }

  /**
   * Parse risk level from Critic review
   */
  private parseRiskLevel(reviewMarkdown: string): RiskLevel | undefined {
    const text = reviewMarkdown.replace(/\r\n/g, '\n');
    const match = text.match(/(^|\n)##\s*Risk\s*\n\s*(low|medium|high)\b/i);
    if (!match?.[2]) return undefined;
    const value = match[2].toLowerCase();
    if (value === 'low' || value === 'medium' || value === 'high') return value;
    return undefined;
  }

  /**
   * Check if Critic should run
   */
  private shouldRunCritic(writerOutput: string): boolean {
    if (!this.config.enabled) return false;
    if (writerOutput.length < this.config.critic.minChars) return false;
    return true;
  }
}

// Singleton instance
let orchestratorInstance: DualBrainOrchestrator | null = null;

export function getOrchestrator(): DualBrainOrchestrator {
  if (!orchestratorInstance) {
    // Load config from localStorage
    const savedConfig = localStorage.getItem('diotec360-dual-brain-config');
    const config = savedConfig ? JSON.parse(savedConfig) : {};
    orchestratorInstance = new DualBrainOrchestrator(config);
  }
  return orchestratorInstance;
}

export function saveOrchestratorConfig(config: Partial<DualBrainConfig>): void {
  const orchestrator = getOrchestrator();
  orchestrator.updateConfig(config);
  localStorage.setItem('diotec360-dual-brain-config', JSON.stringify(orchestrator.getConfig()));
}
