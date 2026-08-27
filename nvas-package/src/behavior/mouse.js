// src/behavior/mouse.js

class MouseCollector {
  constructor() {
    this.clickTimestamps = [];
    this.mouseMovements = [];
    this.lastRecordedTime = 0;
    this.isActive = false;

    this.onMouseMove = this.onMouseMove.bind(this);
    this.onClick = this.onClick.bind(this);
  }

  start() {
    if (this.isActive) return;
    this.isActive = true;
    document.addEventListener('mousemove', this.onMouseMove);
    document.addEventListener('click', this.onClick);
  }

  stop() {
    this.isActive = false;
    document.removeEventListener('mousemove', this.onMouseMove);
    document.removeEventListener('click', this.onClick);
  }

  onMouseMove(event) {
    const currentTime = Date.now();
    // Throttle movement recording (e.g., every 50ms) to avoid massive arrays
    if (currentTime - this.lastRecordedTime >= 50) {
      this.mouseMovements.push({
        x: event.clientX,
        y: event.clientY,
        timestamp: currentTime
      });
      this.lastRecordedTime = currentTime;
    }
  }

  onClick(event) {
    this.clickTimestamps.push(Date.now());
  }

  getData() {
    return {
      clickTimestamps: [...this.clickTimestamps],
      movements: [...this.mouseMovements]
    };
  }

  reset() {
    this.clickTimestamps = [];
    this.mouseMovements = [];
  }
}

module.exports = new MouseCollector();
