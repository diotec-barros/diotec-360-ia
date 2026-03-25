/**
 * Intelligence Harvester - v4.0.0
 * 
 * "The Student Learns from the Masters"
 * 
 * Captures proven code patterns from AI interactions and stores them
 * as training seeds for our sovereign AI.
 * 
 * Architecture:
 * 1. User writes code with AI assistance
 * 2. Judge (Z3) proves correctness mathematically
 * 3. Harvester captures the PROVEN pattern as training data
 * 4. Export as JSONL for fine-tuning
 * 
 * Result: We use billion-dollar AIs to generate perfect training data for free.
 */

export interface TrainingSeed {
  id: string;
  timestamp: number;
  
  // The interaction
  prompt: string;
  aiOutput: string;
  finalCode: string;
  
  // The proof
  judgeVerdict: 'PROVED' | 'UNSAT' | 'UNKNOWN' | 'TIMEOUT';
  z3Proof?: string;
  merkleRoot?: string;
  
  // Metadata
  aiProvider: string;
  aiModel: string;
  
  // Classification
  category: 'financial' | 'security' | 'algorithm' | 'data-structure' | 'other';
  language: string;
  complexity: 'low' | 'medium' | 'high';
  
  // Privacy
  sanitized: boolean;
}

export class IntelligenceHarvester {
  private seeds: TrainingSeed[] = [];
  private maxSeeds: number = 10000;
  private storageKey: string = 'diotec360-training-seeds';

  constructor() {
    this.loadSeeds();
  }

  /**
   * Harvest a proven interaction as training data
   */
  public async harvest(interaction: {
    prompt: string;
    aiOutput: string;
    finalCode: string;
    judgeVerdict: 'PROVED' | 'UNSAT' | 'UNKNOWN' | 'TIMEOUT';
    z3Proof?: string;
    aiProvider: string;
    aiModel: string;
    language: string;
  }): Promise<void> {
    // Only harvest PROVED interactions
    if (interaction.judgeVerdict !== 'PROVED') {
      return;
    }

    // Sanitize sensitive data
    const sanitized = this.sanitize(interaction);

    // Create training seed
    const seed: TrainingSeed = {
      id: this.generateId(sanitized.prompt, sanitized.finalCode),
      timestamp: Date.now(),
      prompt: sanitized.prompt,
      aiOutput: sanitized.aiOutput,
      finalCode: sanitized.finalCode,
      judgeVerdict: interaction.judgeVerdict,
      z3Proof: interaction.z3Proof,
      aiProvider: interaction.aiProvider,
      aiModel: interaction.aiModel,
      category: this.classifyCategory(sanitized.prompt, sanitized.finalCode),
      language: interaction.language,
      complexity: this.assessComplexity(sanitized.finalCode),
      sanitized: true
    };

    // Add to collection
    this.seeds.push(seed);

    // Enforce max limit (keep most recent)
    if (this.seeds.length > this.maxSeeds) {
      this.seeds = this.seeds.slice(-this.maxSeeds);
    }

    // Save to localStorage
    this.saveSeeds();

    // Sync to cloud (if configured)
    await this.syncToCloud(seed);

    console.log(`🧠 Knowledge harvested! (${this.seeds.length} proven patterns)`);
  }

  /**
   * Sanitize sensitive data from code and prompts
   */
  private sanitize(interaction: any): any {
    const patterns = [
      // API Keys
      { regex: /[a-zA-Z0-9_-]{32,}/g, replacement: '[API_KEY]' },
      // Email addresses
      { regex: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, replacement: '[EMAIL]' },
      // Phone numbers
      { regex: /\+?[0-9]{1,4}?[-.\s]?\(?[0-9]{1,3}?\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}/g, replacement: '[PHONE]' },
      // IP addresses
      { regex: /\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b/g, replacement: '[IP_ADDRESS]' },
      // URLs with credentials
      { regex: /https?:\/\/[^:]+:[^@]+@/g, replacement: '[CREDENTIALS]' },
      // Credit card numbers
      { regex: /\b(?:\d{4}[-\s]?){3}\d{4}\b/g, replacement: '[CARD_NUMBER]' }
    ];

    let sanitizedPrompt = interaction.prompt;
    let sanitizedAiOutput = interaction.aiOutput;
    let sanitizedCode = interaction.finalCode;

    patterns.forEach(({ regex, replacement }) => {
      sanitizedPrompt = sanitizedPrompt.replace(regex, replacement);
      sanitizedAiOutput = sanitizedAiOutput.replace(regex, replacement);
      sanitizedCode = sanitizedCode.replace(regex, replacement);
    });

    return {
      prompt: sanitizedPrompt,
      aiOutput: sanitizedAiOutput,
      finalCode: sanitizedCode
    };
  }

  /**
   * Classify the category of the interaction
   */
  private classifyCategory(prompt: string, code: string): TrainingSeed['category'] {
    const text = (prompt + ' ' + code).toLowerCase();

    if (text.match(/\b(bank|payment|transaction|balance|deposit|withdraw|transfer|forex|treasury)\b/)) {
      return 'financial';
    }
    if (text.match(/\b(auth|security|encrypt|decrypt|hash|signature|verify|proof)\b/)) {
      return 'security';
    }
    if (text.match(/\b(sort|search|tree|graph|algorithm|optimize|complexity)\b/)) {
      return 'algorithm';
    }
    if (text.match(/\b(array|list|map|set|queue|stack|data structure)\b/)) {
      return 'data-structure';
    }

    return 'other';
  }

  /**
   * Assess code complexity
   */
  private assessComplexity(code: string): 'low' | 'medium' | 'high' {
    const lines = code.split('\n').length;
    const cyclomaticComplexity = (code.match(/\b(if|for|while|case|catch)\b/g) || []).length;

    if (lines < 20 && cyclomaticComplexity < 5) return 'low';
    if (lines < 100 && cyclomaticComplexity < 15) return 'medium';
    return 'high';
  }

  /**
   * Generate unique ID for seed
   */
  private generateId(prompt: string, code: string): string {
    const str = prompt + code + Date.now().toString();
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash).toString(16).substring(0, 16);
  }

  /**
   * Load seeds from localStorage
   */
  private loadSeeds(): void {
    try {
      const data = localStorage.getItem(this.storageKey);
      if (data) {
        this.seeds = JSON.parse(data);
      }
    } catch (error) {
      console.error('Failed to load training seeds:', error);
      this.seeds = [];
    }
  }

  /**
   * Save seeds to localStorage
   */
  private saveSeeds(): void {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.seeds));
    } catch (error) {
      console.error('Failed to save training seeds:', error);
    }
  }

  /**
   * Sync seed to DIOTEC 360 cloud for global learning
   */
  private async syncToCloud(seed: TrainingSeed): Promise<void> {
    try {
      const publicKey = localStorage.getItem('diotec360-user-public-key');

      if (!publicKey) {
        return; // No identity configured, skip sync
      }

      // Get API URL from environment
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://diotec-360-diotec-360-ia-judge.hf.space';

      // Send to knowledge lattice
      const response = await fetch(`${apiUrl}/api/knowledge/harvest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Sovereign-Key': publicKey
        },
        body: JSON.stringify({
          prompt: seed.prompt,
          writerOutput: seed.aiOutput,
          criticReview: '', // Not applicable for single-brain mode
          finalCode: seed.finalCode,
          judgeVerdict: seed.judgeVerdict,
          z3Proof: seed.z3Proof || '',
          writerProvider: seed.aiProvider,
          writerModel: seed.aiModel,
          criticProvider: seed.aiProvider,
          criticModel: seed.aiModel,
          category: seed.category,
          language: seed.language,
          complexity: seed.complexity
        })
      });

      if (response.ok) {
        const result = await response.json();
        if (result.merkleRoot) {
          seed.merkleRoot = result.merkleRoot;
          this.saveSeeds();
          console.log(`🌐 Synced to cloud: ${result.seedId} (Merkle: ${result.merkleRoot.substring(0, 16)}...)`);
        }
      }
    } catch (error) {
      // Silent fail - local storage is primary
      console.log('Cloud sync skipped:', error);
    }
  }

  /**
   * Export seeds for training (JSONL format)
   */
  public exportForTraining(): Blob {
    // Convert to JSONL format (one JSON per line)
    const lines = this.seeds.map(seed => JSON.stringify({
      prompt: seed.prompt,
      completion: seed.finalCode,
      metadata: {
        category: seed.category,
        language: seed.language,
        complexity: seed.complexity,
        judgeVerdict: seed.judgeVerdict,
        aiModel: seed.aiModel,
        timestamp: seed.timestamp
      }
    }));

    const jsonl = lines.join('\n');
    return new Blob([jsonl], { type: 'application/jsonl' });
  }

  /**
   * Get statistics
   */
  public getStats(): {
    total: number;
    byCategory: Record<string, number>;
    byLanguage: Record<string, number>;
    byComplexity: Record<string, number>;
  } {
    const stats = {
      total: this.seeds.length,
      byCategory: {} as Record<string, number>,
      byLanguage: {} as Record<string, number>,
      byComplexity: {} as Record<string, number>
    };

    this.seeds.forEach(seed => {
      stats.byCategory[seed.category] = (stats.byCategory[seed.category] || 0) + 1;
      stats.byLanguage[seed.language] = (stats.byLanguage[seed.language] || 0) + 1;
      stats.byComplexity[seed.complexity] = (stats.byComplexity[seed.complexity] || 0) + 1;
    });

    return stats;
  }

  /**
   * Get all seeds
   */
  public getSeeds(): TrainingSeed[] {
    return [...this.seeds];
  }

  /**
   * Clear all seeds
   */
  public clearSeeds(): void {
    this.seeds = [];
    this.saveSeeds();
  }

  /**
   * Get seed count
   */
  public getSeedCount(): number {
    return this.seeds.length;
  }
}

// Singleton instance
let harvesterInstance: IntelligenceHarvester | null = null;

export function getHarvester(): IntelligenceHarvester {
  if (!harvesterInstance) {
    harvesterInstance = new IntelligenceHarvester();
  }
  return harvesterInstance;
}
