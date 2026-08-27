// src/behavior/scroll.js

class ScrollCollector {
  constructor() {
    this.scrollData = [];
    this.isActive = false;

    this.onScroll = this.onScroll.bind(this);
  }

  start() {
    if (this.isActive) return;
    this.isActive = true;
    window.addEventListener('scroll', this.onScroll);
  }

  stop() {
    this.isActive = false;
    window.removeEventListener('scroll', this.onScroll);
  }

  onScroll() {
    const timestamp = Date.now();
    const currentScrollPosition = window.scrollY || document.documentElement.scrollTop;

    this.scrollData.push({
      timestamp,
      position: currentScrollPosition
    });
  }

  getData() {
    return {
      scrollEvents: [...this.scrollData]
    };
  }

  reset() {
    this.scrollData = [];
  }
}

module.exports = new ScrollCollector();
