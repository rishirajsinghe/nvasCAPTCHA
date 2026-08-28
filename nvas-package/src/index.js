// src/index.js

const behaviorCollector = require('./behavior/collector');
const featureAggregator = require('./features/aggregator');
const ApiClient = require('./api/client');

class NvasCaptcha {
  constructor() {
    this.apiClient = new ApiClient();
    this.initialized = false;
  }

  /**
   * Initializes behavior tracking.
   * Call this when the page loads.
   */
  init(options = {}) {
    if (this.initialized) return;
    
    if (options.endpoint) {
      this.apiClient = new ApiClient(options.endpoint);
    }
    
    behaviorCollector.startAll();
    this.initialized = true;
    console.log('[NVAS CAPTCHA] Initialized and collecting behavior data.');
  }

  /**
   * Stops tracking behavior and resets collected data.
   */
  stop() {
    behaviorCollector.stopAll();
    behaviorCollector.resetAll();
    this.initialized = false;
  }

  /**
   * Aggregates features and sends them to the backend for verification.
   * Call this when the user performs a critical action (e.g., clicking login).
   * 
   * @returns {Promise<Object>} Verification result with risk score and suggested action.
   */
  async verify() {
    if (!this.initialized) {
      throw new Error('[NVAS CAPTCHA] Must call init() before verify().');
    }

    const features = featureAggregator.aggregate();
    try {
      const result = await this.apiClient.sendFeatures(features);
      return result;
    } catch (error) {
      console.error('[NVAS CAPTCHA] Verification failed:', error);
      throw error;
    }
  }
}

// Export a singleton instance
module.exports = new NvasCaptcha();
