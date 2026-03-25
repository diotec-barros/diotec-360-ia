/**
 * DIOTEC 360 IA - Sovereign SDK (JavaScript)
 * 
 * "Integrity as a Service"
 * 
 * Official JavaScript SDK for integrating
 * mathematical proof verification into any application.
 * 
 * @version 1.0.0
 * @license MIT
 */

class Diotec360SDK {
  constructor(config) {
    this.apiKey = config.apiKey;
    this.baseUrl = config.baseUrl || 'https://api.diotec360.com';
    this.timeout = config.timeout || 30000;
  }

  /**
   * Verify an intent with mathematical proof
   */
  async verify(request) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.baseUrl}/api/sdk/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': this.apiKey,
        },
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        const errorMsg = errorBody.detail || `${response.status} ${response.statusText}`;
        throw new Error(`SDK Error: ${errorMsg}`);
      }

      return await response.json();
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * List all available intents
   */
  async listIntents() {
    const response = await fetch(`${this.baseUrl}/api/sdk/intents`, {
      headers: {
        'X-API-Key': this.apiKey,
      },
    });

    if (!response.ok) {
      throw new Error(`SDK Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Health check
   */
  async health() {
    const response = await fetch(`${this.baseUrl}/api/sdk/health`);
    return await response.json();
  }

  /**
   * Verify a financial transfer
   */
  async verifyTransfer(params) {
    return this.verify({
      intent: 'transfer',
      params,
    });
  }

  /**
   * Verify an escrow transaction
   */
  async verifyEscrow(params) {
    return this.verify({
      intent: 'escrow',
      params,
    });
  }

  /**
   * Verify a multi-signature authorization
   */
  async verifyMultisig(params) {
    return this.verify({
      intent: 'multisig',
      params,
    });
  }

  /**
   * Verify a loan calculation
   */
  async verifyLoan(params) {
    return this.verify({
      intent: 'loan',
      params,
    });
  }

  /**
   * Verify a voting action
   */
  async verifyVote(params) {
    return this.verify({
      intent: 'vote',
      params,
    });
  }

  /**
   * Verify a delivery confirmation
   */
  async verifyDelivery(params) {
    return this.verify({
      intent: 'delivery',
      params,
    });
  }
}

/**
 * Create SDK instance
 */
function createDiotec360SDK(config) {
  return new Diotec360SDK(config);
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { Diotec360SDK, createDiotec360SDK };
}

if (typeof window !== 'undefined') {
  window.Diotec360SDK = Diotec360SDK;
  window.createDiotec360SDK = createDiotec360SDK;
}
