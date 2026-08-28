// src/api/client.js

class ApiClient {
  constructor(endpoint) {
    // Default to the local backend during development
    this.endpoint = endpoint || 'http://127.0.0.1:8000/verify';
  }

  async sendFeatures(features) {
    console.log('[NVAS API Client] Sending features to backend:', this.endpoint);
    
    try {
      const response = await fetch(this.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(features)
      });

      if (!response.ok) {
        throw new Error(`[NVAS API Client] HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('[NVAS API Client] Received verification result:', data);
      return data;
    } catch (error) {
      console.error('[NVAS API Client] Verification failed:', error);
      // Fallback response so the app doesn't crash, but fail safe
      return {
        success: false,
        riskScore: 1.0,
        action: 'block',
        reason: 'Verification request failed'
      };
    }
  }
}

module.exports = ApiClient;
