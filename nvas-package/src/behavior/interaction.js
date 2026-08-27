// src/behavior/interaction.js

class InteractionCollector {
  constructor() {
    this.fieldInteractions = [];
    this.interactionTimestamps = [];
    this.currentFocus = null;
    this.isActive = false;

    this.onFocus = this.onFocus.bind(this);
    this.onBlur = this.onBlur.bind(this);
  }

  start() {
    if (this.isActive) return;
    this.isActive = true;
    document.addEventListener('focus', this.onFocus, true);
    document.addEventListener('blur', this.onBlur, true);
  }

  stop() {
    this.isActive = false;
    document.removeEventListener('focus', this.onFocus, true);
    document.removeEventListener('blur', this.onBlur, true);
  }

  onFocus(event) {
    const target = event.target;
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
      const startTime = Date.now();
      this.interactionTimestamps.push(startTime);
      this.currentFocus = {
        fieldType: target.type || target.tagName.toLowerCase(),
        startTime: startTime
      };
    }
  }

  onBlur(event) {
    const target = event.target;
    if ((target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') && this.currentFocus) {
      const endTime = Date.now();
      this.fieldInteractions.push({
        fieldType: this.currentFocus.fieldType,
        timeSpentMs: endTime - this.currentFocus.startTime
      });
      this.currentFocus = null;
    }
  }

  getData() {
    return {
      interactions: [...this.fieldInteractions],
      interactionTimestamps: [...this.interactionTimestamps]
    };
  }

  reset() {
    this.fieldInteractions = [];
    this.interactionTimestamps = [];
    this.currentFocus = null;
  }
}

module.exports = new InteractionCollector();
