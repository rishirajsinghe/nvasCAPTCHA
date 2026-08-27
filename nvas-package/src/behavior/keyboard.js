// src/behavior/keyboard.js

class KeyboardCollector {
  constructor() {
    this.keyPressCount = 0;
    this.backspaceCount = 0;
    this.repeatedKeyCount = 0;
    
    this.keyHoldData = [];
    this.intervals = [];
    
    this.currentPresses = {}; // Tracks currently held keys by id and start timestamp
    this.lastKeyPressTime = null;
    this.lastKeyPressId = null;
    this.isActive = false;

    this.onKeyDown = this.onKeyDown.bind(this);
    this.onKeyUp = this.onKeyUp.bind(this);
  }

  start() {
    if (this.isActive) return;
    this.isActive = true;
    document.addEventListener('keydown', this.onKeyDown, true);
    document.addEventListener('keyup', this.onKeyUp, true);
  }

  stop() {
    this.isActive = false;
    document.removeEventListener('keydown', this.onKeyDown, true);
    document.removeEventListener('keyup', this.onKeyUp, true);
  }

  onKeyDown(event) {
    const currentTime = Date.now();
    this.keyPressCount += 1;

    // Track backspaces specifically as it indicates hesitation/correction
    if (event.key === 'Backspace') {
      this.backspaceCount += 1;
    }

    // Use keyCode or an anonymous ID to track repetitions without storing the actual character value
    const keyId = event.keyCode || 'unknown'; 
    if (this.lastKeyPressId === keyId) {
      this.repeatedKeyCount += 1;
    }
    this.lastKeyPressId = keyId;

    // Interval between consecutive key presses
    if (this.lastKeyPressTime) {
      this.intervals.push(currentTime - this.lastKeyPressTime);
    }
    this.lastKeyPressTime = currentTime;

    // Track hold start time
    if (!this.currentPresses[keyId]) {
      this.currentPresses[keyId] = currentTime;
    }
  }

  onKeyUp(event) {
    const currentTime = Date.now();
    const keyId = event.keyCode || 'unknown';
    
    if (this.currentPresses[keyId]) {
      const holdDuration = currentTime - this.currentPresses[keyId];
      this.keyHoldData.push(holdDuration);
      delete this.currentPresses[keyId];
    }
  }

  getData() {
    return {
      keyPressCount: this.keyPressCount,
      backspaceCount: this.backspaceCount,
      repeatedKeyCount: this.repeatedKeyCount,
      keyHoldDurations: [...this.keyHoldData],
      keyPressIntervals: [...this.intervals]
    };
  }

  reset() {
    this.keyPressCount = 0;
    this.backspaceCount = 0;
    this.repeatedKeyCount = 0;
    this.keyHoldData = [];
    this.intervals = [];
    this.currentPresses = {};
    this.lastKeyPressTime = null;
    this.lastKeyPressId = null;
  }
}

module.exports = new KeyboardCollector();
